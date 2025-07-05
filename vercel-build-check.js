#!/usr/bin/env node

// Vercel Build Check Script
// This script always returns exit code 1 to force builds
// regardless of file changes

console.log('🚀 Pantheon Physics Swarm - RESET BUILD CHECK');
console.log('==============================================');
console.log('🔄 TRIGGER-005-RESET: Complete setup reset');

const timestamp = new Date().toISOString();
console.log(`Build check timestamp: ${timestamp}`);

// Check if we're in a Vercel build environment
const isVercel = process.env.VERCEL === '1';
const commitSha = process.env.VERCEL_GIT_COMMIT_SHA || 'unknown';
const branch = process.env.VERCEL_GIT_COMMIT_REF || 'unknown';

console.log(`Environment: ${isVercel ? 'Vercel' : 'Local'}`);
console.log(`Branch: ${branch}`);
console.log(`Commit SHA: ${commitSha}`);

// Always exit with code 1 to force builds
console.log('🔥 FORCING BUILD - Exit code 1');
console.log('📋 Framework Preset: Other');
console.log('⚙️  Custom vercel.json configuration active');
console.log('🚀 This ensures every push triggers a new deployment');

process.exit(1); 