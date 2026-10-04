import * as esbuild from 'esbuild';
import { mkdirSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const distRoot = join(__dirname, 'dist');

const functions = ['chat', 'upload', 'history', 'connect', 'disconnect'];

// Node.js 18+ Lambda runtimes include AWS SDK v3.
const sharedExternals = ['@aws-sdk/*'];

rmSync(distRoot, { recursive: true, force: true });

await Promise.all(
  functions.map(async (name) => {
    const outdir = join(distRoot, name);
    mkdirSync(outdir, { recursive: true });

    await esbuild.build({
      entryPoints: [join(__dirname, 'src', name, 'handler.ts')],
      outfile: join(outdir, 'handler.js'),
      bundle: true,
      platform: 'node',
      target: 'node20',
      format: 'cjs',
      sourcemap: false,
      minify: true,
      // chat: pg comes from the Lambda layer
      external: name === 'chat' ? [...sharedExternals, 'pg', 'pg-native'] : sharedExternals,
      logLevel: 'info',
    });
  })
);

console.log(`Built ${functions.length} Lambda bundles → ${distRoot}`);
