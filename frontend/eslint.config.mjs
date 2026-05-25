import nextVitals from 'eslint-config-next/core-web-vitals'
import prettier from 'eslint-config-prettier'

const eslintConfig = [
  {
    ignores: ['.next/**', 'node_modules/**', 'coverage/**', 'dist/**', 'build/**'],
  },
  ...nextVitals,
  prettier,
  {
    rules: {
      'prefer-const': 'error',
      'no-console': ['warn', { allow: ['warn', 'error'] }],
    },
  },
]

export default eslintConfig
