shader_type canvas_item;
render_mode blend_add;
uniform float progress : hint_range(0.0, 1.0) = 0.0;
uniform float aspect = 1.0;
uniform float strength = 1.0;

void fragment() {
	vec2 p = (UV - vec2(0.5)) * vec2(aspect, 1.0);
	float radius = length(p);
	float t = clamp(progress, 0.0, 1.0);
	float ring = exp(-abs(radius - t * 0.48) * 110.0) * (1.0 - t);
	float echo = exp(-abs(radius - t * 0.34) * 70.0) * (1.0 - t) * 0.5;
	float flash = exp(-radius * 13.0) * pow(1.0 - t, 7.0);
	vec3 light = vec3(0.12, 0.9, 0.95) * (ring + echo) + vec3(1.0, 0.65, 0.25) * flash;
	COLOR = vec4(light * strength, (ring + echo + flash) * strength);
}
