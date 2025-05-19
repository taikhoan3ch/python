'use client';

import { Canvas } from '@react-three/fiber';
import { Suspense } from 'react';
import Scene from '@/components/Scene';
import Loading from '@/components/Loading';

export default function Home() {
  return (
    <main className="h-screen w-full">
      <Suspense fallback={<Loading />}>
        <Canvas
          camera={{ position: [0, 0, 5], fov: 75 }}
          className="bg-black"
        >
          <Scene />
        </Canvas>
      </Suspense>
    </main>
  );
}
