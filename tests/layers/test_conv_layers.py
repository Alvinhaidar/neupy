from itertools import product
from collections import namedtuple

import numpy as np

from neupy.utils import asfloat, as_tuple
from neupy import layers
from neupy.layers.convolutions import conv_output_shape

from base import BaseTestCase


class ConvLayersTestCase(BaseTestCase):
    def test_convolution_params(self):
        weight_shape = (6, 1, 2, 2)
        bias_shape = (6,)

        input_layer = layers.Input((1, 5, 5))
        conv_layer = layers.Convolution((6, 2, 2))

        input_layer > conv_layer
        conv_layer.initialize()

        self.assertEqual(weight_shape, conv_layer.weight.get_value().shape)
        self.assertEqual(bias_shape, conv_layer.bias.get_value().shape)

    def test_conv_shapes(self):
        border_modes = [
            'valid', 'full', 'half',
            4, 5,
            (6, 3), (4, 4), (1, 1)
        ]
        strides = [(1, 1), (2, 1), (2, 2)]
        x = asfloat(np.random.random((20, 2, 12, 11)))

        for stride, border_mode in product(strides, border_modes):
            input_layer = layers.Input((2, 12, 11))
            conv_layer = layers.Convolution((5, 3, 4),
                                            border_mode=border_mode,
                                            stride_size=stride)

            input_layer > conv_layer
            conv_layer.initialize()

            y = conv_layer.output(x).eval()
            actual_output_shape = as_tuple(y.shape[1:])

            self.assertEqual(actual_output_shape, conv_layer.output_shape,
                             msg='border_mode={}'.format(border_mode))

    def test_valid_strides(self):
        Case = namedtuple("Case", "stride_size expected_output")
        testcases = (
            Case(stride_size=(4, 4), expected_output=(4, 4)),
            Case(stride_size=(4,), expected_output=(4, 1)),
            Case(stride_size=4, expected_output=(4, 4)),
        )

        for testcase in testcases:
            conv_layer = layers.Convolution((1, 2, 3),
                                            stride_size=testcase.stride_size)
            msg = "Input stride size: {}".format(testcase.stride_size)
            self.assertEqual(testcase.expected_output, conv_layer.stride_size,
                             msg=msg)

    def test_invalid_strides(self):
        invalid_strides = (
            (4, 4, 4),
            -10,
            (-5, -5),
            (-5, 5),
            (-5, 0),
        )

        for stride_size in invalid_strides:
            msg = "Input stride size: {}".format(stride_size)
            with self.assertRaises(ValueError, msg=msg):
                layers.Convolution((1, 2, 3), stride_size=stride_size)

    def test_valid_border_mode(self):
        valid_border_modes = ('valid', 'full', 'half', (5, 3), 4, (4, 0))
        for border_mode in valid_border_modes:
            layers.Convolution((1, 2, 3), border_mode=border_mode)

    def test_invalid_border_mode(self):
        invalid_border_modes = ('invalid mode', -10, (10, -5))

        for border_mode in invalid_border_modes:
            msg = "Input border mode: {}".format(border_mode)
            with self.assertRaises(ValueError, msg=msg):
                layers.Convolution((1, 2, 3), border_mode=border_mode)

    def test_conv_output_shape_func_exceptions(self):
        with self.assertRaises(ValueError):
            conv_output_shape(dimension_size=5, filter_size=5, border_mode=5,
                              stride='not int')

        with self.assertRaises(ValueError):
            conv_output_shape(dimension_size=5, filter_size='not int',
                              border_mode=5, stride=5)

        with self.assertRaises(ValueError):
            conv_output_shape(dimension_size=5, filter_size=5,
                              border_mode='invalid value', stride=5)
