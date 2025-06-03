# M-Star Classification Frontend

This project is a frontend application for an M-star classification system, built with Quasar Framework (Vue.js and Vite).

## Project Setup

### Prerequisites

- Node.js (version specified in `package.json` - e.g., ^16 || ^18 || ^20)
- npm or yarn

### Installation

1. Navigate to the `mstar-classification-frontend` directory:
   ```bash
   cd mstar-classification-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

### Development Server

To start the development server with hot-reloading:

```bash
npm run dev
# or
yarn dev
```

This will typically open the application in your default web browser at `http://localhost:8080` (or the port specified in `quasar.config.js`).

### Linting and Formatting

- To lint files:
  ```bash
  npm run lint
  # or
  yarn lint
  ```

- To format files:
  ```bash
  npm run format
  # or
  yarn format
  ```

### Building for Production

To build the application for production:

```bash
npm run build
# or
yarn build
```

This will create a `dist` folder with the production-ready files.

## Project Structure

- `public/`: Static assets.
- `src/`: Main application source code.
  - `assets/`: Static assets like images, fonts (processed by Vite).
  - `boot/`: Quasar boot files (for initialization code).
  - `components/`: Reusable Vue components.
  - `css/`: Global CSS and SCSS variables.
  - `i18n/`: Internationalization language files.
  - `layouts/`: Layout components (e.g., MainLayout with header, drawer).
  - `pages/`: Page components (views for different routes).
  - `router/`: Vue Router configuration.
  - `stores/`: Pinia store modules (if used).
  - `App.vue`: Root Vue component.
  - `main.ts`: Main entry point for the application.
- `quasar.config.js`: Quasar framework configuration.
- `vite.config.ts`: Vite build tool configuration.
- `tsconfig.json`: TypeScript configuration.
- `package.json`: Project dependencies and scripts. 