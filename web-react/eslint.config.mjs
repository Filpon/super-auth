import { fileURLToPath } from 'node:url';
import path from 'node:path';
import js from '@eslint/js';
import eslintConfigPrettier from 'eslint-config-prettier/flat';
import eslintReact from 'eslint-plugin-react';
import eslintReactHooks from 'eslint-plugin-react-hooks';
import eslintReactRefresh from 'eslint-plugin-react-refresh';
import prettierPlugin from 'eslint-plugin-prettier';
import simpleImportSort from 'eslint-plugin-simple-import-sort';
import globals from 'globals';
import tseslint from 'typescript-eslint';
const filename = fileURLToPath(import.meta.url);
const dirname = path.dirname(filename);
export default tseslint.config(
  {
    ignores: [
      'dist',
      'coverage',
      'eslint.config.mjs',
      'App.test.js',
      '**/.svelte-kit',
      '**/.vercel',
      '**/.yarn',
      '**/build',
      '**/package',
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2020,
      },
      parserOptions: {
        project: ['tsconfig.json', 'tsconfig.node.json'],
        tsconfigRootDir: dirname,
      },
    },
    plugins: {
      react: eslintReact,
      'react-hooks': eslintReactHooks,
      'react-refresh': eslintReactRefresh,
      prettier: prettierPlugin,
      'simple-import-sort': simpleImportSort,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    rules: {
      'no-console': 'off',
      eqeqeq: 'off',
      'prefer-const': 'error',
      'prettier/prettier': 'error',
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      'react/jsx-curly-brace-presence': [
        'warn',
        { props: 'never', children: 'never' },
      ],
      'react/function-component-definition': [
        'warn',
        { namedComponents: 'arrow-function' },
      ],
      'react/self-closing-comp': [
        'error',
        { component: true, html: true },
      ],
      'max-lines': ['warn', { max: 124 }],
      'max-params': ['error', 3],
      '@typescript-eslint/no-explicit-any': 'off',
      'simple-import-sort/imports': 'error',
      'simple-import-sort/exports': 'error',
    },
  },
  // ESLint - Prettier correlation
  eslintConfigPrettier,
);