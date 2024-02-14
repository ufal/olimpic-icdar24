#!/usr/bin/env python3
import argparse
import contextlib
import datetime
import json
import os
import pickle
import re
from typing import Self
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")  # Report only TF errors by default

import numpy as np
import tensorflow as tf

import ser_metric

parser = argparse.ArgumentParser()
parser.add_argument("--augment", default="h:8", type=str, help="Augmentation type.")
parser.add_argument("--batch_size", default=64, type=int, help="Batch size.")
parser.add_argument("--cnn_dim", default=32, type=int, help="CNN dim at original resolution.")
parser.add_argument("--cnn_resblocks", default=2, type=int, help="CNN ResNet blocks per layer.")
parser.add_argument("--cnn_stages", default=4, type=int, help="CNN layers.")
parser.add_argument("--decay", default="cos", choices=["none", "cos"], help="Decay type.")
parser.add_argument("--dev", default=[], nargs="*", type=str, help="Dev dataset paths.")
parser.add_argument("--dropout", default=0.2, type=float, help="Dropout.")
parser.add_argument("--epochs", default=50, type=int, help="Number of epochs.")
parser.add_argument("--evaluation_each", default=50, type=int, help="Evaluate each epoch.")
parser.add_argument("--evaluation_from", default=50, type=int, help="Evaluate from epoch.")
parser.add_argument("--exp", default="", type=str, help="Exp name.")
parser.add_argument("--height", default=192, type=int, help="Image height.")
parser.add_argument("--load", default=None, type=str, help="Load weights from model and predict.")
parser.add_argument("--max_predict_length", default=700, type=int, help="Maximum prediction sequence length.")
parser.add_argument("--max_train_length", default=500, type=int, help="Maximum training sequence length.")
parser.add_argument("--rnn_dim", default=192, type=int, help="RNN dimension.")
parser.add_argument("--rnn_layers", default=2, type=int, help="RNN layers.")
parser.add_argument("--rnn_layers_decoder", default=1, type=int, help="RNN decoder layers.")
parser.add_argument("--seed", default=42, type=int, help="Random seed.")
parser.add_argument("--test", default=[], nargs="*", type=str, help="Test dataset paths.")
parser.add_argument("--threads", default=4, type=int, help="Maximum number of threads to use.")
parser.add_argument("--train", default=None, type=str, help="Training dataset path.")
parser.add_argument("--timestep_width", default=16, type=int, help="Timestep width.")
parser.add_argument("--verbose", default=1, type=int, help="Verbosity")
parser.add_argument("--visualize_only", default=False, action="store_true", help="Visualize only.")


class LMXDataset:
    def __init__(self, description: str, args: argparse.Namespace, train_dataset: Self|None = None):
        self._args = args
        self._tf_dataset = None

        self.path, *self._transformations = description.split(",")
        self.basename = os.path.splitext(os.path.basename(self.path))[0]
        with open(f"{self.path}.pickle", "rb") as data_file:
            self.data = pickle.load(data_file)

        if train_dataset is None:
            self.tags = ["<unk>"]
            self.tags_map = {"<unk>": 0}
        else:
            self.tags = train_dataset.tags
            self.tags_map = train_dataset.tags_map

        for entry in self.data:
            lmx = entry[f"lmx"]
            seq = []
            for part in lmx.split():
                if part not in self.tags_map:
                    if train_dataset is None:
                        self.tags_map[part] = len(self.tags)
                        self.tags.append(part)
                    else:
                        part = "<unk>"
                seq.append(self.tags_map[part])
            entry["seq"] = np.array(seq, dtype=np.int32)

        # Shuffle train, because it is sorted by authors, and we use only a small window in tf.data pipeline.
        if train_dataset is None:
            np.random.RandomState(42).shuffle(self.data)

        # Print statistics
        if train_dataset is None:
            print("Tags: {}".format(len(self.tags)))
        print("Loaded dataset {}, {} examples, {:.2f} avg length".format(
            self.basename, len(self.data), np.mean([len(entry["seq"]) for entry in self.data])))

    def save_tags(self, path: str) -> None:
        with open(path, "w") as tags_file:
            for tag in self.tags:
                print(tag, file=tags_file)

    @staticmethod
    def from_tags(path: str) -> Self:
        dataset = LMXDataset.__new__(LMXDataset)
        dataset.tags = []
        with open(path, "r") as tags_file:
            for line in tags_file:
                dataset.tags.append(line.rstrip("\r\n"))
        dataset.tags_map = {tag: index for index, tag in enumerate(dataset.tags)}
        return dataset

    def tf_dataset(self, training: bool = False) -> tf.data.Dataset:
        if self._tf_dataset is not None:
            return self._tf_dataset

        if training:
            # Prepare augmentation operations
            self._generator = tf.random.Generator.from_seed(self._args.seed)
            if match := re.search(r"rotate:([\d.]+)", self._args.augment):
                self._augment_rotation = tf.keras.layers.RandomRotation(
                    float(match.group(1)) / 360, fill_mode="constant", interpolation="bilinear", seed=self._args.seed, fill_value=1.0)

        def generator():
            for entry in self.data:
                yield entry["image"], entry["seq"]
        def prepare_example(image, tags):
            image = tf.image.convert_image_dtype(tf.image.decode_image(image, channels=1, expand_animations=False), tf.float32)
            for transformation, *parameters in map(lambda part: part.split(":"), self._transformations):
                if transformation == "threshold":
                    l, r, *rest = parameters
                    l, r, smooth = float(l), float(r), rest.count("smooth")
                    if not smooth:
                        image = tf.cast(image >= l, tf.float32) * tf.cast(image <= r, tf.float32) * image + tf.cast(image > r, tf.float32)
                    else:
                        image = tf.clip_by_value((image - l) / (r - l), 0., 1.)
                elif transformation:
                    raise ValueError(f"The transformation '{transformation}' is unknown.")
            image = tf.image.resize(image, size=[self._args.height, tf.int32.max], preserve_aspect_ratio=True, antialias=True)
            return image, tags
        def augment(image, tags):
            for augmentation, *parameters in map(lambda part: part.split(":"), self._args.augment.split(",")):
                if self._generator.uniform([], 0, 1) >= 0.5:
                    continue
                if augmentation == "h":
                    a = int(parameters[0])
                    image = tf.pad(image, [[0, 0], [a, 0], [0, 0]], constant_values=1.0)[:, self._generator.uniform([], 0, 2 * a + 1, dtype=tf.int32):]
                elif augmentation == "v":
                    a = int(parameters[0])
                    image = tf.pad(image, [[a, a], [0, 0], [0, 0]], constant_values=1.0)[self._generator.uniform([], 0, 2 * a + 1, dtype=tf.int32):]
                    image = image[:self._args.height]
                elif augmentation == "rotate":
                    image = self._augment_rotation(image, training=True)
                elif augmentation == "b":
                    l, u = map(float, parameters[:2])
                    image = tf.clip_by_value(tf.image.adjust_brightness(image, self._generator.uniform([], l, u)), 0., 1.)
                elif augmentation == "c":
                    l, u = map(float, parameters[:2])
                    image = tf.clip_by_value(tf.image.adjust_contrast(image, 2 ** self._generator.uniform([], l, u)), 0., 1.)
                elif augmentation == "n":
                    p = float(parameters[0])
                    mask = tf.cast(self._generator.uniform(tf.shape(image), 0, 1) >= self._generator.uniform([], 0, p), tf.float32)
                    image = mask * image + (1 - mask) * (1 - image)
                elif augmentation == "en3":
                    p = float(parameters[0])
                    mask = tf.nn.avg_pool2d(image[tf.newaxis], 3, 1, padding="SAME")[0]
                    mask = tf.cast((mask <= 0.1) | (mask >= 0.9), tf.float32)
                    mask = mask + (1 - mask) * tf.cast(self._generator.uniform(tf.shape(mask), 0, 1) >= self._generator.uniform([], 0, p), tf.float32)
                    image = mask * image + (1 - mask) * (1 - image)
                elif augmentation == "de":
                    d = self._generator.uniform([], -np.pi / 2, np.pi / 2)
                    x, y = tf.cos(d), 0.5 * tf.sin(d)
                    moved = tf.raw_ops.ImageProjectiveTransformV3(
                        images=image[tf.newaxis], transforms=[[1., 0., x, 0., 1., y, 0., 0.]],
                        output_shape=tf.shape(image)[:2], fill_value=1.0, interpolation="BILINEAR")[0]
                    if self._generator.uniform([], 0, 1) >= 0.5:
                        image = tf.math.maximum(image, moved)
                    else:
                        image = tf.clip_by_value(image + moved - 1, 0., 1.)
                elif augmentation:
                    raise ValueError(f"The augmentation '{augmentation}' is unknown.")
            return image, tags

        dataset = tf.data.Dataset.from_generator(generator, output_signature=(
            tf.TensorSpec(shape=(), dtype=tf.string), tf.TensorSpec(shape=(None,), dtype=tf.int32)))
        dataset = dataset.cache()
        dataset = dataset.apply(tf.data.experimental.assert_cardinality(sum(1 for _ in dataset)))
        dataset = dataset.shuffle(5_000, seed=self._args.seed) if training else dataset
        dataset = dataset.map(prepare_example, num_parallel_calls=tf.data.AUTOTUNE)
        dataset = dataset.map(augment, num_parallel_calls=tf.data.AUTOTUNE) if training and self._args.augment else dataset
        dataset = dataset.ragged_batch(self._args.batch_size)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        self._tf_dataset = dataset
        return dataset


class Model(tf.keras.Model):
    BOS = EOS = 0

    class WithAttention(tf.keras.layers.AbstractRNNCell):
        """A class adding Bahdanau attention to the given RNN cell."""
        def __init__(self, cells, attention_dim):
            super().__init__()
            self._cells = cells
            self._project_encoder_layer = tf.keras.layers.Dense(attention_dim)
            self._project_decoder_layer = tf.keras.layers.Dense(attention_dim)
            self._output_layer = tf.keras.layers.Dense(1)

        @property
        def state_size(self):
            return tuple(cell.state_size for cell in self._cells)

        def setup_memory(self, encoded):
            self._encoded = encoded
            self._encoded_projected = self._project_encoder_layer(encoded)

        def call(self, inputs, states):
            projected = self._encoded_projected + tf.expand_dims(self._project_decoder_layer(tf.concat(states[0], axis=1)), axis=1)
            weights = tf.nn.softmax(self._output_layer(tf.tanh(projected)), axis=1)
            attention = tf.reduce_sum(self._encoded * weights, axis=1)
            inputs, new_states = tf.concat([inputs, attention], axis=1), []
            for i, (cell, state) in enumerate(zip(self._cells, states)):
                outputs, new_state = cell(inputs, state)
                inputs = outputs if i == 0 else inputs + outputs
                new_states.append(new_state)
            return outputs, tuple(new_states)

    def __init__(self, args: argparse.Namespace, dataset: LMXDataset) -> None:
        super().__init__()
        self._args = args

        # Define encoder
        inputs = tf.keras.layers.Input(shape=[args.height, None, 1], dtype=tf.float32, ragged=True)

        hidden = inputs.to_tensor()
        hidden = tf.keras.layers.Conv2D(args.cnn_dim, 3, 1, "same", use_bias=False)(hidden)
        for i in range(args.cnn_stages):
            filters = min(args.rnn_dim, args.cnn_dim * (1 << i))
            residual = tf.keras.layers.Conv2D(filters, 3, 2, "same", use_bias=False)(hidden)
            residual = tf.keras.layers.BatchNormalization()(residual)
            hidden = tf.keras.layers.Conv2D(filters, 3, 2, "same", use_bias=False)(hidden)
            hidden = tf.keras.layers.BatchNormalization()(hidden)
            hidden = tf.keras.layers.ReLU()(hidden)
            hidden = tf.keras.layers.Conv2D(filters, 3, 1, "same", use_bias=False)(hidden)
            hidden = tf.keras.layers.BatchNormalization()(hidden)
            hidden += residual
            hidden = tf.keras.layers.ReLU()(hidden)
            for _ in range(args.cnn_resblocks - 1):
                residual = hidden
                hidden = tf.keras.layers.Conv2D(filters, 3, 1, "same", use_bias=False)(hidden)
                hidden = tf.keras.layers.BatchNormalization()(hidden)
                hidden = tf.keras.layers.ReLU()(hidden)
                hidden = tf.keras.layers.Conv2D(filters, 3, 1, "same", use_bias=False)(hidden)
                hidden = tf.keras.layers.BatchNormalization()(hidden)
                hidden += residual
                hidden = tf.keras.layers.ReLU()(hidden)

        hidden = tf.transpose(hidden, [0, 2, 1, 3])
        hidden = tf.reshape(hidden, [tf.shape(hidden)[0], tf.shape(hidden)[1], hidden.shape[2] * hidden.shape[3]])

        remaining = args.timestep_width // (1 << args.cnn_stages)
        if remaining < 1:
            raise ValueError("Inconsistent settings of timestep width {} and cnn stages {}".format(
                args.timestep_width, args.cnn_stages))
        if remaining > 1:
            hidden = tf.pad(hidden, [[0, 0], [0, (-tf.shape(hidden)[1]) % remaining], [0, 0]])
            hidden = tf.reshape(
                hidden, [tf.shape(hidden)[0], tf.shape(hidden)[1] // remaining, hidden.shape[2] * remaining])

        hidden = tf.keras.layers.Dropout(args.dropout)(hidden)

        reduced_row_lengths = inputs.row_lengths(axis=2)[:, :1].to_tensor()[:, 0]
        reduced_row_lengths = (reduced_row_lengths + args.timestep_width - 1) // args.timestep_width
        mask = tf.sequence_mask(reduced_row_lengths)
        for layer in range(args.rnn_layers):
            residual = hidden
            rnn_layer = tf.keras.layers.LSTM(args.rnn_dim, return_sequences=True)
            hidden = tf.keras.layers.Bidirectional(rnn_layer, merge_mode="sum")(hidden, mask=mask)
            hidden = tf.keras.layers.Dropout(args.dropout)(hidden)
            if layer: hidden += residual

        self.encoder = tf.keras.Model(inputs=inputs, outputs=hidden)

        # Decoder layers
        self._target_embedding = tf.keras.layers.Embedding(1 + len(dataset.tags), args.rnn_dim)
        self._target_rnn = tf.keras.layers.RNN(
            Model.WithAttention([tf.keras.layers.LSTMCell(args.rnn_dim) for _ in range(args.rnn_layers_decoder)], args.rnn_dim), return_sequences=True)
        self._target_output_layer = tf.keras.layers.Dense(1 + len(dataset.tags))

        # Compilation
        if not args.load:
            lr = 1e-3
            if args.decay == "cos":
                lr = tf.optimizers.schedules.CosineDecay(lr, args.train_batches * args.epochs)
            elif args.decay != "none":
                raise ValueError("Unknown decay '{}'".format(args.decay))

            self.compile(optimizer=tf.optimizers.Adam(lr, jit_compile=False),
                         loss=tf.losses.SparseCategoricalCrossentropy(from_logits=True))

            self.tb_callback = tf.keras.callbacks.TensorBoard(args.logdir)

    def decoder_training(self, encoded: tf.Tensor, targets: tf.Tensor) -> tf.Tensor:
        self._target_rnn.cell.setup_memory(encoded)

        decoder_input = tf.concat([tf.fill([tf.shape(targets)[0], 1], Model.BOS), targets[:, :-1]], axis=-1)
        hidden = self._target_embedding(decoder_input)
        hidden = self._target_rnn(hidden)
        hidden = self._target_output_layer(hidden)
        return hidden

    @tf.function
    def decoder_inference(self, encoded: tf.Tensor, max_length: tf.Tensor) -> tf.Tensor:
        self._target_rnn.cell.setup_memory(encoded)

        batch_size = tf.shape(encoded)[0]
        index = tf.zeros([], tf.int32)
        inputs = tf.fill([batch_size], Model.BOS)
        states = self._target_rnn.cell.get_initial_state(batch_size=batch_size, dtype=tf.float32)
        results = tf.TensorArray(tf.int32, size=max_length)
        result_lengths = tf.fill([batch_size], max_length)
        while tf.math.logical_and(index < max_length, tf.math.reduce_any(result_lengths == max_length)):
            hidden = self._target_embedding(inputs)
            hidden, states = self._target_rnn.cell(hidden, states)
            hidden = self._target_output_layer(hidden)
            predictions = tf.argmax(hidden, axis=-1, output_type=tf.int32)
            results = results.write(index, predictions)
            result_lengths = tf.where((predictions == Model.EOS) & (result_lengths > index), index, result_lengths)
            inputs = predictions
            index += 1
        results = tf.RaggedTensor.from_tensor(tf.transpose(results.stack()), lengths=result_lengths)
        return results

    def train_step(self, data):
        x, y = data
        y = tf.concat([y + 1, tf.fill([tf.shape(y)[0], 1], Model.EOS)], axis=-1)[:, :self._args.max_train_length]
        with tf.GradientTape() as tape:
            encoded = self.encoder(x, training=True)
            y_pred = self.decoder_training(encoded, y)
            loss = self.compiled_loss(y.values, y_pred.values)
        self.optimizer.minimize(loss, self.trainable_variables, tape=tape)
        return {metric.name: metric.result() for metric in self.compiled_loss.metrics}

    def predict_step(self, data):
        if isinstance(data, tuple):
            data = data[0]
        encoded = self.encoder(data, training=False)
        y_pred = self.decoder_inference(encoded, self._args.max_predict_length)
        return y_pred - 1


def main(params: list[str] | None = None) -> None:
    args = parser.parse_args(params)

    # If supplied, load configuration from a trained model
    if args.load:
        with open(os.path.join(args.load, "options.json"), mode="r") as options_file:
            args = argparse.Namespace(**{k: v for k, v in json.load(options_file).items() if k not in [
                "dev", "exp", "load", "test", "threads", "verbose"]})
            args = parser.parse_args(params, namespace=args)
        args.logdir = args.exp if args.exp else args.load
    else:
        args.script = os.path.basename(__file__)
        # Create logdir name
        args.logdir = os.path.join("logs", "{}{}-{}".format(
            args.exp + (args.exp and "-"),
            os.path.basename(globals().get("__file__", "notebook")),
            datetime.datetime.now().strftime("%y%m%d_%H%M%S"),
        ))
        os.makedirs(args.logdir, exist_ok=True)
        with open(os.path.join(args.logdir, "options.json"), mode="w") as options_file:
            json.dump(vars(args), options_file, sort_keys=True, ensure_ascii=False, indent=2)

    # Set the random seed and the number of threads.
    tf.keras.utils.set_random_seed(args.seed)
    tf.config.threading.set_inter_op_parallelism_threads(args.threads)
    tf.config.threading.set_intra_op_parallelism_threads(args.threads)

    if args.load:
        train = LMXDataset.from_tags(os.path.join(args.load, "tags.txt"))
    else:
        train = LMXDataset(args.train, args)
        train.save_tags(os.path.join(args.logdir, "tags.txt"))
    devs = [LMXDataset(dev, args, train) for dev in args.dev]
    tests = [LMXDataset(test, args, train) for test in args.test]

    if args.visualize_only:
        # Visualize the generated data
        os.makedirs(args.logdir, exist_ok=True)
        for dataset in [train] + devs + tests:
            c = 0
            for x, y in dataset.tf_dataset(training=dataset == train):
                while c < 100 and x.shape[0]:
                    with open(f"{args.logdir}/{dataset.basename}-{c}.png", "wb") as png_file:
                        png_file.write(tf.image.encode_png(tf.cast(x[0].to_tensor() * 255, tf.uint8)).numpy())
                        x = x[1:]
                        c += 1
                if c >= 100:
                    break
            with open(f"{args.logdir}/_{dataset.basename}.html", "w") as html_file:
                print(f"<html><body><h1>{dataset.basename}</h1>", file=html_file)
                for c in range(100):
                    print(f"<div><img src='{dataset.basename}-{c}.png'></div><hr>", file=html_file)
                print("</body></html>", file=html_file)
        return

    strategy_scope = tf.distribute.MirroredStrategy().scope() if len(tf.config.list_physical_devices("GPU")) > 1 else contextlib.nullcontext()
    with strategy_scope:
        # Create the network and train
        if not args.load:
            args.train_batches = len(train.tf_dataset(training=True))
        model = Model(args, train)

    class Evaluator(tf.keras.callbacks.Callback):
        @staticmethod
        def predict(dataset, tag):
            predicted_tags = model.predict(dataset.tf_dataset(), verbose=0)
            predicted_strings = []
            for tags in predicted_tags:
                predicted_strings.append(" ".join(train.tags[tag] for tag in tags.numpy()))
            with open(os.path.join(args.logdir, "{}.{}.lmx".format(dataset.basename, tag)), mode="w") as out_file:
                print(*predicted_strings, sep="\n", file=out_file)
            gold = [entry["lmx"] for entry in dataset.data]
            metrics = ser_metric.ser_metric(gold, predicted_strings)
            with open(os.path.join(args.logdir, "{}.{}.lmx.eval".format(dataset.basename, tag)), mode="w") as eval_file:
                for metric, value in metrics.items():
                    print("{}: {:.3f}%".format(metric, value), file=eval_file)
            return metrics

        def on_epoch_end(self, epoch, logs=None):
            if epoch + 1 < args.epochs and (epoch + 1 < args.evaluation_from or (epoch + 1) % args.evaluation_each != 0):
                return
            for dataset in devs + (tests if epoch + 1 == args.epochs else []):
                for metric, value in self.predict(dataset, str(epoch + 1)).items():
                    logs[f"{dataset.basename}_{metric}"] = value

    if args.load:
        model.decoder_inference(model.encoder(tf.RaggedTensor.from_tensor(tf.ones([1, args.height, 128, 1], dtype=tf.float32), ragged_rank=2)), 1)
        model.built = True
        model.load_weights(os.path.join(args.load, "weights.h5"))
        os.makedirs(args.logdir, exist_ok=True)
        for dataset in devs + tests:
            for metric, value in Evaluator.predict(dataset, tag="predicted").items():
                print("{} {}: {:.3f}%".format(dataset.basename, metric, value))
    else:
        model.fit(train.tf_dataset(training=True), epochs=args.epochs, callbacks=[Evaluator(), model.tb_callback], verbose=args.verbose)
        model.save_weights(os.path.join(args.logdir, "weights.h5"))


if __name__ == "__main__":
    main([] if "__file__" not in globals() else None)
