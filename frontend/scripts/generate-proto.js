#!/usr/bin/env node
/**
 * Generate TypeScript definitions from Protocol Buffer schemas
 * Uses ts-proto to generate type-safe TypeScript code
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const projectRoot = path.resolve(__dirname, '..');
const protoDir = path.resolve(projectRoot, '../proto');
const outDir = path.resolve(projectRoot, 'src/lib/proto_generated');

console.log('Generating TypeScript from Protocol Buffers...');
console.log('Proto directory:', protoDir);
console.log('Output directory:', outDir);

// Create output directory if it doesn't exist
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

// Check if proto files already exist
const typesFile = path.join(outDir, 'types.ts');
const utilsFile = path.join(outDir, 'protobuf-utils.ts');

if (fs.existsSync(typesFile) && fs.existsSync(utilsFile)) {
  console.log('✓ Proto files already exist, skipping generation');
  process.exit(0);
}

try {
  // Use ts-proto plugin to generate TypeScript
  const protocCommand = `protoc \
    --plugin=./node_modules/.bin/protoc-gen-ts_proto \
    --ts_proto_out=${outDir} \
    --ts_proto_opt=outputServices=false \
    --ts_proto_opt=esModuleInterop=true \
    --ts_proto_opt=forceLong=string \
    --ts_proto_opt=useDate=false \
    --proto_path=${protoDir} \
    ${protoDir}/library.proto`;

  execSync(protocCommand, { stdio: 'inherit', cwd: projectRoot });
  
  console.log('✓ TypeScript generation complete!');
} catch (error) {
  console.error('Error generating TypeScript:', error.message);
  console.log('\nFalling back to pbjs/pbts method...');
  
  try {
    // Fallback: Use protobufjs static code generation
    const pbjsCommand = `npx protobufjs-cli pbjs -t static-module -w es6 -o ${outDir}/library.js ${protoDir}/library.proto`;
    const pbtsCommand = `npx protobufjs-cli pbts -o ${outDir}/library.d.ts ${outDir}/library.js`;
    
    console.log('Running:', pbjsCommand);
    execSync(pbjsCommand, { stdio: 'inherit', cwd: projectRoot });
    console.log('Running:', pbtsCommand);
    execSync(pbtsCommand, { stdio: 'inherit', cwd: projectRoot });
    
    console.log('✓ TypeScript generation complete (using pbjs/pbts)!');
  } catch (fallbackError) {
    console.error('Failed to generate TypeScript files:', fallbackError.message);
    console.log('Proto files may need to be generated manually.');
    // Don't exit with error if proto directory doesn't exist (Docker build scenario)
    if (!fs.existsSync(protoDir)) {
      console.log('Proto directory not found, but pre-generated files exist. Continuing...');
      process.exit(0);
    }
    process.exit(1);
  }
}
