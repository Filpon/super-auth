import { fileURLToPath } from 'url';
import * as path from 'path';
import { fixupPluginRules } from '@eslint/compat';
import js from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import { FlatCompat } from '@eslint/eslintrc';
import eslintReact from 'eslint-plugin-react';
import eslintReactHooks from 'eslint-plugin-react-hooks';
import eslintReactRefresh from 'eslint-plugin-react-refresh';
import prettierPlugin from 'eslint-plugin-prettier';
import eslintTs from 'typescript-eslint';
import eslintConfigPrettier from 'eslint-config-prettier';

const filename = fileURLToPath(import.meta.url);
const dirname = path.dirname(filename);
const compat = new FlatCompat({
  baseDirectory: dirname,
  recommendedConfig: eslintTs.configs.recommended,
});

function legacyPlugin(name, alias = name) {
  const plugin = compat.plugins(name)[0]?.plugins?.[alias];

  if (!plugin) {
    throw new Error(`Unable to resolve plugin ${name} and/or alias ${alias}`);
  }

  return fixupPluginRules(plugin);
}

/** @type {import('eslint').Linter.Config[]} */
export default tseslint.config(
  {
    plugins: {
      '@typescript-eslint': tseslint.plugin,
      react: eslintReact,
      'react-hooks': eslintReactHooks,
      'react-refresh': eslintReactRefresh,
      prettier: prettierPlugin,
      import: legacyPlugin('eslint-plugin-import', 'import'),
    },
  },
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
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2020,
      },
      parserOptions: {
        project: ['tsconfig.json', 'tsconfig.node.json'],
      },
    },
  },
  {
    files: ['**/*.{ts,tsx}'],
    settings: {
      react: {
        version: 'detect',
      },
    },
    rules: {
      'no-console': 'off',
      eqeqeq: 'off',
      ...prettierPlugin.configs.recommended.rules,
      ...eslintConfigPrettier.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      'prefer-const': 'error',
      'react/jsx-curly-brace-presence': [
        'warn',
        { props: 'never', children: 'never' },
      ],
      'react/function-component-definition': [
        'warn',
        { namedComponents: 'arrow-function' },
      ],
      'react/self-closing-comp': ['error', { component: true, html: true }],
      'max-lines': ['warn', { max: 124 }],
      'max-params': ['error', 3],
      '@typescript-eslint/no-explicit-any': 'off', // Disable the rule
      'import/named': 'error',
      'import/default': 'error',
      'import/namespace': 'error',
      'import/no-unresolved': 'error',
      'import/no-extraneous-dependencies': ['warn', { devDependencies: true }],
      'import/order': [
        'error',
        {
          groups: [
            'builtin',
            'external',
            'internal',
            'parent',
            'sibling',
            'index',
          ],
          'newlines-between': 'always',
        },
      ],
      'import/prefer-default-export': 'off',
    },
  },
);
