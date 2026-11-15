"use client";
import { useEffect, useRef, useState } from "react";

// A spherical diffusion flame in microgravity, drawn the way CFI-G shows it on the ISS: a thin blue reaction shell
// around a small porous burner fed by a tube, brighter at its edge (an optically thin shell is seen through more
// gas at the limb), a faint patchy soot glow inside, and no buoyant plume because there is no "up".
const FRAG = `
precision highp float;
uniform vec2 u_res;
uniform vec2 u_center;
uniform float u_radius;
uniform float u_time;
uniform float u_ignite;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}
float fbm(vec2 p) { float s = 0.0, a = 0.5; for (int i = 0; i < 4; i++) { s += a * noise(p); p *= 2.03; a *= 0.5; } return s; }

// Path length through a spherical shell between radii ri and ro, seen at projected distance r.
float shell(float r, float ri, float ro) {
  float a = sqrt(max(ro * ro - r * r, 0.0));
  float b = sqrt(max(ri * ri - r * r, 0.0));
  return 2.0 * (a - b);
}

float capsule(vec2 p, vec2 a, vec2 b, float w) {
  vec2 pa = p - a, ba = b - a;
  float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
  return length(pa - ba * h) - w;
}

void main() {
  vec2 frag = gl_FragCoord.xy;
  vec2 p = (frag - u_center) / u_radius;          // flame units: shell radius ~ 1
  float r = length(p);
  float ang = atan(p.y, p.x);
  float t = u_time;

  // Ignition: the shell grows out of the burner, then breathes slowly as the real flames do.
  float grow = mix(0.18, 1.0, u_ignite);
  float breath = 1.0 + 0.035 * sin(t * 0.42) + 0.015 * sin(t * 1.13 + 1.7);
  float wrinkle = 0.010 * (fbm(vec2(ang * 2.2, t * 0.18)) - 0.5);
  float R = grow * breath * (1.0 + wrinkle);
  float w = 0.055 * R;

  // Blue chemiluminescent reaction zone.
  float blue = shell(r, R - w, R + w) / (2.0 * sqrt(2.0 * R * w) + 1e-4);
  // Soft halo around the shell.
  float halo = exp(-pow((r - R) / (0.30 * R), 2.0)) * 0.07;
  // Patchy soot glow inside the shell, slow and faint.
  float sootR = 0.74 * R;
  float soot = shell(r, sootR - 0.11 * R, sootR + 0.11 * R) / (2.0 * R);
  soot *= smoothstep(0.55, 0.85, fbm(p * 2.2 + vec2(t * 0.05, -t * 0.03)));

  float lit = u_ignite;
  vec3 col = vec3(0.0);
  col += vec3(0.20, 0.42, 1.0) * pow(blue, 1.6) * 1.15 * lit;
  col += vec3(0.30, 0.55, 1.0) * halo * lit;
  col += vec3(1.0, 0.50, 0.14) * soot * 0.30 * lit;

  // Tone map so the brightest edge reads as near-white blue, like an overexposed ISS camera.
  col = 1.0 - exp(-col * 1.6);

  // Porous burner and its feed tube (in front of the back half of the shell).
  vec2 dir = normalize(vec2(-0.62, -0.78));
  float tube = capsule(p, dir * 0.06, dir * 6.0, 0.024);
  float ball = length(p) - 0.065;
  float body = min(tube, ball);
  float mask = 1.0 - smoothstep(0.0, 0.012, body);
  float rim = exp(-abs(body) * 60.0) * 0.6;
  vec3 metal = vec3(0.10, 0.11, 0.13) + vec3(0.25, 0.42, 0.85) * rim * lit * smoothstep(1.4 * R, 0.0, r);
  col = mix(col, metal + col * 0.35, mask);

  // Space: near-black with a faint vignette and sparse fixed stars.
  vec2 uv = frag / u_res;
  vec3 bg = mix(vec3(0.020, 0.027, 0.043), vec3(0.008, 0.011, 0.018), length(uv - 0.5) * 1.2);
  vec2 cell = floor(frag / 3.0);
  float star = step(0.9985, hash(cell)) * hash(cell + 7.0) * 0.55;
  bg += vec3(star) * (1.0 - smoothstep(0.0, 1.6, r) * 0.9);
  col = bg + col;

  // Dither against banding.
  col += (hash(frag + t) - 0.5) / 255.0;
  gl_FragColor = vec4(col, 1.0);
}`;

const VERT = `attribute vec2 a; void main() { gl_Position = vec4(a, 0.0, 1.0); }`;

export default function FlameCanvas({ className = "" }: { className?: string }) {
  const ref = useRef<HTMLCanvasElement>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const canvas = ref.current!;
    const gl = canvas.getContext("webgl", { antialias: false, alpha: false, powerPreference: "low-power" });
    if (!gl) {
      setFailed(true);
      return;
    }
    const compile = (type: number, src: string) => {
      const s = gl.createShader(type)!;
      gl.shaderSource(s, src);
      gl.compileShader(s);
      return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null;
    };
    const vs = compile(gl.VERTEX_SHADER, VERT);
    const fs = compile(gl.FRAGMENT_SHADER, FRAG);
    const prog = gl.createProgram()!;
    if (!vs || !fs) {
      setFailed(true);
      return;
    }
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
      setFailed(true);
      return;
    }
    gl.useProgram(prog);
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, "a");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const u = (n: string) => gl.getUniformLocation(prog, n);
    const uRes = u("u_res"), uCenter = u("u_center"), uRadius = u("u_radius"), uTime = u("u_time"), uIgnite = u("u_ignite");

    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let w = 0, h = 0;
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.75);
      w = Math.max(1, Math.round(canvas.clientWidth * dpr));
      h = Math.max(1, Math.round(canvas.clientHeight * dpr));
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
    };
    const geometry = () => {
      const wide = w / h > 1.15;
      // Wide screens: flame on the right third; tall screens: flame low, between the buttons and the facts.
      return wide
        ? { cx: w * 0.73, cy: h * 0.5, r: Math.min(h * 0.25, w * 0.15) }
        : { cx: w * 0.68, cy: h * 0.255, r: Math.min(w * 0.23, h * 0.13) };
    };

    let raf = 0, visible = true, start = performance.now();
    const draw = (now: number) => {
      const t = reduce ? 20 : (now - start) / 1000;
      const k = reduce ? 1 : Math.min(1, t / 2.4);
      const ignite = 1 - Math.pow(1 - k, 3); // ease-out ignition, once
      const g = geometry();
      gl.uniform2f(uRes, w, h);
      gl.uniform2f(uCenter, g.cx, g.cy);
      gl.uniform1f(uRadius, g.r);
      gl.uniform1f(uTime, t + 3);
      gl.uniform1f(uIgnite, ignite);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    };
    const loop = (now: number) => {
      draw(now);
      if (visible && !document.hidden) raf = requestAnimationFrame(loop);
    };
    const kick = () => {
      cancelAnimationFrame(raf);
      if (reduce) draw(performance.now());
      else raf = requestAnimationFrame(loop);
    };
    const ro = new ResizeObserver(() => {
      resize();
      if (reduce) draw(performance.now());
    });
    ro.observe(canvas);
    const io = new IntersectionObserver(([e]) => {
      visible = e.isIntersecting;
      if (visible) kick();
    });
    io.observe(canvas);
    const onVis = () => !document.hidden && kick();
    document.addEventListener("visibilitychange", onVis);
    resize();
    start = performance.now();
    kick();
    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
    };
  }, []);

  return (
    <div className={`flame ${className}`} aria-hidden="true">
      {failed ? <div className="flame-fallback" /> : <canvas ref={ref} />}
    </div>
  );
}
