import tensorflow as tf


def save_keras_model(model: tf.keras.Model):
    config = tf.keras.saving.serialize_keras_object(model)
    weights = model.get_weights()
    optimizer_config = model.optimizer.get_config()

    return config, weights, optimizer_config


def load_keras_model(config, weights, optimizer_config):
    model = tf.keras.saving.deserialize_keras_object(config)
    model.set_weights(weights)
    optimizer = tf.keras.optimizers.get(optimizer_config["name"]).from_config(optimizer_config)
    model.compile(optimizer=optimizer, loss=tf.keras.losses.get(model.loss))

    return model
