import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

export default function ArcReactor({ state = 'idle', audioLevel = 0, size = 360 }) {
  const containerRef = useRef(null);
  const stateRef = useRef(state);
  const audioLevelRef = useRef(audioLevel);

  const [coreStats, setCoreStats] = useState({
    flux: 4.2,
    temp: 3.8,
    efficiency: 99.8
  });

  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  useEffect(() => {
    audioLevelRef.current = audioLevel;
  }, [audioLevel]);

  // Live stat fluctuation reacting dynamically to voice and audio amplitude
  useEffect(() => {
    const interval = setInterval(() => {
      const amp = audioLevelRef.current / 100;
      setCoreStats({
        flux: +(4.2 + amp * 3.8 + (Math.random() * 0.2 - 0.1)).toFixed(2),
        temp: +(3.8 + amp * 2.4 + (Math.random() * 0.1 - 0.05)).toFixed(2),
        efficiency: +(99.8 - (stateRef.current === 'thinking' ? 0.6 : 0) + amp * 0.2 + (Math.random() * 0.1 - 0.05)).toFixed(1)
      });
    }, 100);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // --- 1. THREE.JS SCENE SETUP ---
    const width = size;
    const height = size;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 18;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.35;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // --- 2. LIGHTING RIG ---
    const ambientLight = new THREE.AmbientLight(0x0a192f, 2.5);
    scene.add(ambientLight);

    const coreLight = new THREE.PointLight(0x00f0ff, 8, 30);
    coreLight.position.set(0, 0, 1.5);
    scene.add(coreLight);

    const rimLight = new THREE.DirectionalLight(0xffffff, 2.2);
    rimLight.position.set(5, 10, 8);
    scene.add(rimLight);

    const backGlow = new THREE.PointLight(0x0088ff, 5, 32);
    backGlow.position.set(0, 0, -4);
    scene.add(backGlow);

    // Master Group for 3D Autonomous Rotation
    const reactorGroup = new THREE.Group();
    scene.add(reactorGroup);

    // --- 3. MATERIALS PALETTE ---
    const colorThemes = {
      idle: {
        primary: 0x00f0ff,
        secondary: 0x0066ff,
        core: 0xffffff,
        emissive: 0x00d2ff,
        lightColor: 0x00f0ff
      },
      thinking: {
        primary: 0xffb700,
        secondary: 0xff4400,
        core: 0xffffff,
        emissive: 0xffaa00,
        lightColor: 0xff9900
      },
      speaking: {
        primary: 0x00ff9d,
        secondary: 0x00a8ff,
        core: 0xffffff,
        emissive: 0x00ffaa,
        lightColor: 0x00ff88
      },
      guardrail_alert: {
        primary: 0xff0055,
        secondary: 0x990022,
        core: 0xffffff,
        emissive: 0xff1144,
        lightColor: 0xff0044
      }
    };

    // --- 4. GEOMETRIES & MESHES ---

    // A. Outer Metallic Heavy Titanium Housing
    const outerBezelGeo = new THREE.TorusGeometry(6.4, 0.45, 24, 80);
    const outerBezelMat = new THREE.MeshStandardMaterial({
      color: 0x111625,
      metalness: 0.92,
      roughness: 0.15,
      emissive: 0x002244,
      emissiveIntensity: 0.25
    });
    const outerBezel = new THREE.Mesh(outerBezelGeo, outerBezelMat);
    reactorGroup.add(outerBezel);

    // B. Outer Segmented Ring with Hash Marks
    const ringSegmentsGroup = new THREE.Group();
    const segmentCount = 36;
    for (let i = 0; i < segmentCount; i++) {
      const angle = (i / segmentCount) * Math.PI * 2;
      const isMajor = i % 3 === 0;
      const segGeo = new THREE.BoxGeometry(0.12, isMajor ? 0.55 : 0.3, 0.2);
      const segMat = new THREE.MeshStandardMaterial({
        color: isMajor ? 0x00f0ff : 0x004488,
        emissive: isMajor ? 0x00f0ff : 0x002244,
        emissiveIntensity: isMajor ? 0.9 : 0.3,
        metalness: 0.8
      });
      const segMesh = new THREE.Mesh(segGeo, segMat);
      segMesh.position.x = Math.cos(angle) * 6.4;
      segMesh.position.y = Math.sin(angle) * 6.4;
      segMesh.rotation.z = angle + Math.PI / 2;
      ringSegmentsGroup.add(segMesh);
    }
    reactorGroup.add(ringSegmentsGroup);

    // C. 10 Toroidal Copper/Palladium Electromagnet Coils
    const coilsGroup = new THREE.Group();
    const coilCount = 10;
    const coilMeshes = [];
    const coilCoreTubeGeo = new THREE.TorusGeometry(5.2, 0.18, 16, 60);
    const coilCoreTubeMat = new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      emissive: 0x00f0ff,
      emissiveIntensity: 1.2,
      transparent: true,
      opacity: 0.85
    });
    const coilCoreTube = new THREE.Mesh(coilCoreTubeGeo, coilCoreTubeMat);
    coilsGroup.add(coilCoreTube);

    for (let i = 0; i < coilCount; i++) {
      const angle = (i / coilCount) * Math.PI * 2;
      const blockGroup = new THREE.Group();

      // Coil Base Block
      const blockGeo = new THREE.BoxGeometry(0.7, 1.1, 0.85);
      const blockMat = new THREE.MeshStandardMaterial({
        color: 0x161b26,
        metalness: 0.95,
        roughness: 0.1
      });
      const block = new THREE.Mesh(blockGeo, blockMat);
      blockGroup.add(block);

      // Copper Coil Wrap Rings
      for (let w = -0.3; w <= 0.3; w += 0.15) {
        const wrapGeo = new THREE.TorusGeometry(0.48, 0.04, 12, 24);
        const wrapMat = new THREE.MeshStandardMaterial({
          color: 0xdf7a28,
          metalness: 0.85,
          roughness: 0.25,
          emissive: 0x552200,
          emissiveIntensity: 0.4
        });
        const wrap = new THREE.Mesh(wrapGeo, wrapMat);
        wrap.position.z = w;
        blockGroup.add(wrap);
      }

      // Neon Emitter Window
      const windowGeo = new THREE.BoxGeometry(0.35, 0.6, 0.9);
      const windowMat = new THREE.MeshBasicMaterial({
        color: 0x00f0ff
      });
      const winMesh = new THREE.Mesh(windowGeo, windowMat);
      blockGroup.add(winMesh);

      blockGroup.position.x = Math.cos(angle) * 5.2;
      blockGroup.position.y = Math.sin(angle) * 5.2;
      blockGroup.rotation.z = angle + Math.PI / 2;

      coilsGroup.add(blockGroup);
      coilMeshes.push({ blockGroup, winMesh, index: i });
    }
    reactorGroup.add(coilsGroup);

    // D. Counter-Rotating Inner Gimbal Rings
    const gimbalGroup1 = new THREE.Group();
    const gimbalGeo1 = new THREE.TorusGeometry(3.6, 0.12, 16, 60);
    const gimbalMat1 = new THREE.MeshStandardMaterial({
      color: 0x00aaff,
      emissive: 0x0088ff,
      emissiveIntensity: 0.6,
      metalness: 0.9
    });
    const gimbal1 = new THREE.Mesh(gimbalGeo1, gimbalMat1);
    gimbalGroup1.add(gimbal1);

    // Teeth on Gimbal 1
    for (let i = 0; i < 24; i++) {
      const angle = (i / 24) * Math.PI * 2;
      const toothGeo = new THREE.BoxGeometry(0.08, 0.25, 0.15);
      const toothMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
      const tooth = new THREE.Mesh(toothGeo, toothMat);
      tooth.position.x = Math.cos(angle) * 3.6;
      tooth.position.y = Math.sin(angle) * 3.6;
      tooth.rotation.z = angle;
      gimbalGroup1.add(tooth);
    }
    reactorGroup.add(gimbalGroup1);

    const gimbalGroup2 = new THREE.Group();
    const gimbalGeo2 = new THREE.TorusGeometry(2.5, 0.1, 16, 50);
    const gimbalMat2 = new THREE.MeshStandardMaterial({
      color: 0x00ffff,
      emissive: 0x00ffff,
      emissiveIntensity: 0.8,
      metalness: 0.85
    });
    const gimbal2 = new THREE.Mesh(gimbalGeo2, gimbalMat2);
    gimbalGroup2.add(gimbal2);
    reactorGroup.add(gimbalGroup2);

    // E. Central Arc Energy Core (Multi-Layer Polyhedral Core)
    const coreSphereGeo = new THREE.SphereGeometry(1.2, 32, 32);
    const coreSphereMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.95
    });
    const coreSphere = new THREE.Mesh(coreSphereGeo, coreSphereMat);
    reactorGroup.add(coreSphere);

    // Quantum Icosahedron Energy Cage
    const icosaGeo = new THREE.IcosahedronGeometry(1.65, 0);
    const icosaMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: true,
      transparent: true,
      opacity: 0.85
    });
    const icosaCage = new THREE.Mesh(icosaGeo, icosaMat);
    reactorGroup.add(icosaCage);

    // Inner Triangular Palladium Insignia
    const triGroup = new THREE.Group();
    const triShape = new THREE.Shape();
    const r = 0.95;
    for (let i = 0; i < 3; i++) {
      const angle = (i * 2 * Math.PI) / 3 - Math.PI / 2;
      const tx = Math.cos(angle) * r;
      const ty = Math.sin(angle) * r;
      if (i === 0) triShape.moveTo(tx, ty);
      else triShape.lineTo(tx, ty);
    }
    triShape.closePath();
    const triGeo = new THREE.ShapeGeometry(triShape);
    const triMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      wireframe: true
    });
    const triMesh = new THREE.Mesh(triGeo, triMat);
    triMesh.position.z = 0.1;
    triGroup.add(triMesh);
    reactorGroup.add(triGroup);

    // F. Swirling 3D Energy Spark Particle System (350 Quantum Particles)
    const particleCount = 350;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    const particleVelocities = [];

    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const rad = 1.8 + Math.random() * 4.8;
      const z = (Math.random() - 0.5) * 2.5;

      particlePositions[i * 3] = Math.cos(theta) * rad;
      particlePositions[i * 3 + 1] = Math.sin(theta) * rad;
      particlePositions[i * 3 + 2] = z;

      particleVelocities.push({
        angle: theta,
        radius: rad,
        speed: (0.01 + Math.random() * 0.025) * (Math.random() > 0.5 ? 1 : -1),
        zOffset: z,
        zSpeed: (Math.random() - 0.5) * 0.02
      });
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

    const particleMat = new THREE.PointsMaterial({
      color: 0x00f0ff,
      size: 0.18,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending
    });
    const particleSystem = new THREE.Points(particleGeo, particleMat);
    reactorGroup.add(particleSystem);

    // --- 5. ANIMATION LOOP ---
    let animId;
    let clock = new THREE.Clock();
    let smoothedAudio = 0;

    const animate = () => {
      const delta = clock.getDelta();
      const time = clock.getElapsedTime();
      const curState = stateRef.current;
      const curAudio = audioLevelRef.current;

      // High-fidelity voice waveform smoothing with snappy attack & smooth decay
      const targetAmp = (curAudio / 100);
      const lerpFactor = targetAmp > smoothedAudio ? 0.35 : 0.12;
      smoothedAudio += (targetAmp - smoothedAudio) * lerpFactor;
      const voiceImpact = Math.pow(smoothedAudio, 1.15);

      // Autonomous 3D floating gyroscope rotation (NO mouse stop / interference)
      reactorGroup.rotation.y = Math.sin(time * 0.6) * (0.12 + voiceImpact * 0.15);
      reactorGroup.rotation.x = Math.cos(time * 0.45) * (0.08 + voiceImpact * 0.12);

      // Dynamic rotation speed accelerating with voice modulation
      const baseSpeed = (curState === 'thinking' ? 2.5 : curState === 'speaking' ? 1.6 : 1.0) * (1.0 + voiceImpact * 2.2);

      // Component Rotations
      outerBezel.rotation.z += 0.003 * baseSpeed;
      ringSegmentsGroup.rotation.z -= 0.005 * baseSpeed;
      coilsGroup.rotation.z += 0.004 * baseSpeed;
      gimbalGroup1.rotation.z -= 0.015 * baseSpeed;
      gimbalGroup2.rotation.z += 0.022 * baseSpeed;
      gimbalGroup2.rotation.x = Math.sin(time * 2.5) * (0.2 + voiceImpact * 0.3);
      gimbalGroup2.rotation.y = Math.cos(time * 2.5) * (0.2 + voiceImpact * 0.3);

      icosaCage.rotation.x += 0.02 * baseSpeed;
      icosaCage.rotation.y += 0.025 * baseSpeed;
      icosaCage.rotation.z += 0.015 * baseSpeed;

      triGroup.rotation.z -= 0.014 * baseSpeed;

      // Highly Responsive Pulsing Scale & Voice Impact Expansion
      const idlePulse = Math.sin(time * 4) * 0.05;
      const pulse = idlePulse + voiceImpact * 0.52;
      const coreScale = 1.0 + pulse;
      coreSphere.scale.set(coreScale, coreScale, coreScale);
      icosaCage.scale.set(coreScale * 1.12, coreScale * 1.12, coreScale * 1.12);
      triGroup.scale.set(1.0 + voiceImpact * 0.35, 1.0 + voiceImpact * 0.35, 1.0 + voiceImpact * 0.35);

      // Dynamic Color Theme & Light Flare Updates
      const theme = colorThemes[curState] || colorThemes.idle;
      coreLight.color.setHex(theme.lightColor);
      coreLight.intensity = 7 + voiceImpact * 25;
      backGlow.intensity = 4 + voiceImpact * 18;
      
      particleMat.color.setHex(theme.primary);
      particleMat.size = 0.18 + voiceImpact * 0.25;
      
      coilCoreTubeMat.color.setHex(theme.primary);
      coilCoreTubeMat.emissive.setHex(theme.emissive);
      coilCoreTubeMat.emissiveIntensity = 1.2 + voiceImpact * 3.0;
      
      icosaMat.color.setHex(theme.primary);
      gimbalMat1.emissive.setHex(theme.secondary);
      gimbalMat1.emissiveIntensity = 0.6 + voiceImpact * 1.8;
      gimbalMat2.color.setHex(theme.primary);
      gimbalMat2.emissiveIntensity = 0.8 + voiceImpact * 2.2;
      outerBezelMat.emissive.setHex(theme.secondary);
      outerBezelMat.emissiveIntensity = 0.25 + voiceImpact * 1.4;

      // Dynamic Swirling 3D Particles reacting to voice
      const positions = particleSystem.geometry.attributes.position.array;
      for (let i = 0; i < particleCount; i++) {
        const vel = particleVelocities[i];
        vel.angle += vel.speed * baseSpeed * (1 + voiceImpact * 3.2);
        vel.zOffset += vel.zSpeed * (1 + voiceImpact * 2.0);
        if (Math.abs(vel.zOffset) > (2.5 + voiceImpact * 1.5)) vel.zSpeed *= -1;

        const dynamicRad = vel.radius + Math.sin(time * 3 + i) * (0.15 + voiceImpact * 0.85);
        positions[i * 3] = Math.cos(vel.angle) * dynamicRad;
        positions[i * 3 + 1] = Math.sin(vel.angle) * dynamicRad;
        positions[i * 3 + 2] = vel.zOffset;
      }
      particleSystem.geometry.attributes.position.needsUpdate = true;

      // Sequential Coil Glow Wave reacting to voice energy
      const wavePos = (time * (3 + voiceImpact * 6)) % coilCount;
      coilMeshes.forEach((coil) => {
        const dist = Math.abs(coil.index - wavePos);
        const glow = Math.max(0.3, 1.0 - (dist % coilCount) * 0.2) + voiceImpact * 1.6;
        coil.winMesh.material.color.setHex(theme.primary);
      });

      renderer.render(scene, camera);
      animId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animId);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [size]);

  return (
    <div className="relative flex flex-col items-center justify-center select-none group pointer-events-none">
      {/* Outer Holographic HUD Ring Brackets */}
      <div
        style={{ width: `${size + 40}px`, height: `${size + 40}px` }}
        className="absolute pointer-events-none rounded-full border border-cyan-500/15 flex items-center justify-center animate-spin-slow"
      >
        <div className="absolute top-0 w-3 h-3 border-t-2 border-l-2 border-cyan-400" />
        <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-cyan-400" />
        <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-cyan-400" />
        <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-cyan-400" />
      </div>

      {/* Outer Ambient Radial Glow Backdrop pulsing with voice */}
      <div
        style={{
          width: `${size * (1.15 + (audioLevelRef.current / 100) * 0.4)}px`,
          height: `${size * (1.15 + (audioLevelRef.current / 100) * 0.4)}px`,
          opacity: 0.3 + (audioLevelRef.current / 100) * 0.5
        }}
        className={`absolute rounded-full pointer-events-none transition-all duration-150 blur-3xl ${
          state === 'thinking'
            ? 'bg-amber-500/50'
            : state === 'speaking'
            ? 'bg-emerald-400/50'
            : state === 'guardrail_alert'
            ? 'bg-rose-500/60'
            : 'bg-cyan-500/40'
        }`}
      />

      {/* Three.js WebGL 3D Arc Reactor Canvas */}
      <div
        ref={containerRef}
        style={{ width: `${size}px`, height: `${size}px` }}
        className="relative z-10 pointer-events-none drop-shadow-[0_0_35px_rgba(0,240,255,0.45)]"
      />

      {/* Floating 3D Telemetry Overlay Badges */}
      <div className="absolute -bottom-4 z-20 flex items-center gap-3 px-4 py-1.5 rounded-xl bg-slate-950/80 border border-cyan-500/30 backdrop-blur-md shadow-[0_0_20px_rgba(6,182,212,0.25)] font-mono text-[11px] pointer-events-auto">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_rgba(6,182,212,1)]" />
          <span className="text-slate-400 uppercase">FLUX:</span>
          <span className="text-cyan-300 font-bold">{coreStats.flux} GW</span>
        </div>
        <div className="w-[1px] h-3 bg-slate-800" />
        <div className="flex items-center gap-1.5">
          <span className="text-slate-400 uppercase">TEMP:</span>
          <span className="text-amber-300 font-bold">{coreStats.temp} MK</span>
        </div>
        <div className="w-[1px] h-3 bg-slate-800" />
        <div className="flex items-center gap-1.5">
          <span className="text-slate-400 uppercase">EFF:</span>
          <span className="text-emerald-300 font-bold">{coreStats.efficiency}%</span>
        </div>
      </div>
    </div>
  );
}
