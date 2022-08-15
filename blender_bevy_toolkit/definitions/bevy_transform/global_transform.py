from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
    rust_types,
)


@register_component
class GlobalTransform(ComponentBase):
    def encode(config, obj):
        """Returns a Component representing this component

        {
        "type": "bevy_transform::components::global_transform::GlobalTransform",
        "tuple_struct": [
          {
            "type": "glam::f32::affine3a::Affine3A",
            "struct": {
              "matrix3": {
                "type": "glam::f32::sse2::mat3a::Mat3A",
                "struct": {
                  "x_axis": {
                    "type": "glam::f32::sse2::vec3a::Vec3A",
                    "struct": {
                      "x": {
                        "type": "f32",
                        "value": 1.0,
                      },
                      "y": {
                        "type": "f32",
                        "value": 0.0,
                      },
                      "z": {
                        "type": "f32",
                        "value": 0.0,
                      },
                    },
                  },
                  "y_axis": {
                    "type": "glam::f32::sse2::vec3a::Vec3A",
                    "struct": {
                      "x": {
                        "type": "f32",
                        "value": 0.0,
                      },
                      "y": {
                        "type": "f32",
                        "value": 1.0,
                      },
                      "z": {
                        "type": "f32",
                        "value": 0.0,
                      },
                    },
                  },
                  "z_axis": {
                    "type": "glam::f32::sse2::vec3a::Vec3A",
                    "struct": {
                      "x": {
                        "type": "f32",
                        "value": 0.0,
                      },
                      "y": {
                        "type": "f32",
                        "value": 0.0,
                      },
                      "z": {
                        "type": "f32",
                        "value": 1.0,
                      },
                    },
                  },
                },
              },
              "translation": {
                "type": "glam::f32::sse2::vec3a::Vec3A",
                "struct": {
                  "x": {
                    "type": "f32",
                    "value": 0.0,
                  },
                  "y": {
                    "type": "f32",
                    "value": 0.0,
                  },
                  "z": {
                    "type": "f32",
                    "value": 0.0,
                  },
                },
              },
            },
          },
        ],
      },
        """

        # If Object has a mesh, then the exported gltf would already have the transform data
        # therefore no need to add the transform to the .scn file.
        if obj.type in ["MESH"]:

          x_axis = [1, 0, 0, 0]
          y_axis = [0, 1, 0, 0]
          z_axis = [0, 0, 1, 0]
          w_axis = [0, 0, 0, 1]

        else:
          transform = obj.matrix_world
          x_axis = [transform[0][0], transform[0]
                    [1], transform[0][2], transform[0][3]]
          y_axis = [transform[1][0], transform[1]
                    [1], transform[1][2], transform[1][3]]
          z_axis = [transform[2][0], transform[2]
                    [1], transform[2][2], transform[2][3]]
          w_axis = [transform[3][0], transform[3]
                    [1], transform[3][2], transform[3][3]]
                    

        return rust_types.Map(
            type="bevy_transform::components::global_transform::GlobalTransform",
            tuple_struct=rust_types.List(
                rust_types.Map(
                    type="glam::f32::affine3a::Affine3A",
                    struct=rust_types.Map(
                        matrix3=rust_types.Map(
                            type="glam::f32::sse2::mat3a::Mat3A",
                            struct=rust_types.Map(
                                x_axis=rust_types.Map(
                                    type="glam::f32::sse2::vec3a::Vec3A",
                                    struct=rust_types.Map(
                                        x=rust_types.F32(x_axis[0]),
                                        y=rust_types.F32(x_axis[1]),
                                        z=rust_types.F32(x_axis[2]),
                                    )
                                ),
                                y_axis=rust_types.Map(
                                    type="glam::f32::sse2::vec3a::Vec3A",
                                    struct=rust_types.Map(
                                        x=rust_types.F32(y_axis[0]),
                                        y=rust_types.F32(y_axis[1]),
                                        z=rust_types.F32(y_axis[2]),
                                    )
                                ),
                                z_axis=rust_types.Map(
                                    type="glam::f32::sse2::vec3a::Vec3A",
                                    struct=rust_types.Map(
                                        x=rust_types.F32(z_axis[0]),
                                        y=rust_types.F32(z_axis[1]),
                                        z=rust_types.F32(z_axis[2]),
                                    )
                                )
                            )
                        ),
                        translation=rust_types.Map(
                            type="glam::f32::sse2::vec3a::Vec3A",
                            struct=rust_types.Map(
                                x=rust_types.F32(w_axis[0]),
                                y=rust_types.F32(w_axis[1]),
                                z=rust_types.F32(w_axis[2]),
                            )
                        )
                    )
                ),
            ),
        )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return hasattr(obj, "matrix_world")

    def can_add(obj):
        return False

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass
