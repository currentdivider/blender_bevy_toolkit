from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
    rust_types,
)


@register_component
class Transform(ComponentBase):
    def encode(config, obj):
        """Returns a Component representing this component
       {
            "type": "bevy_transform::components::transform::Transform",
            "struct": {
                "translation": {
                    "type": "glam::f32::vec3::Vec3",
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
                "rotation": {
                    "type": "glam::f32::sse2::quat::Quat",
                    "value": (0.0,
                    0.0,
                    0.0,
                    1.0),
                },
                "scale": {
                    "type": "glam::f32::vec3::Vec3",
                    "struct": {
                        "x": {
                            "type": "f32",
                            "value": 1.0,
                        },
                        "y": {
                            "type": "f32",
                            "value": 1.0,
                        },
                        "z": {
                            "type": "f32",
                            "value": 1.0,
                        },
                    },
                },
            },
        }
        """
        transform = obj.matrix_world
        if obj.parent is None:
            transform = obj.matrix_world
        else:
            transform = obj.matrix_local

        position, rotation, scale = transform.decompose()

        return rust_types.Map(
            type="bevy_transform::components::transform::Transform",
            struct=rust_types.Map(
                translation=rust_types.Map(
                    type="glam::f32::vec3::Vec3",
                    struct=rust_types.Map(
                        x=rust_types.F32(position[0]),
                        y=rust_types.F32(position[2]),
                        z=rust_types.F32(position[1]),
                    )
                ),
                rotation=rust_types.Quat(rotation),
                scale=rust_types.Map(
                    type="glam::f32::vec3::Vec3",
                    struct=rust_types.Map(
                        x=rust_types.F32(scale.x),
                        y=rust_types.F32(scale.y),
                        z=rust_types.F32(scale.z),
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
