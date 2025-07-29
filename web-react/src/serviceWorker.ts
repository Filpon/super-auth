const isLocalhost = Boolean(
  window.location.hostname === 'localhost' ||
    window.location.hostname === '[::1]' ||
    window.location.hostname.match(
      /^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/,
    ),
);

interface Config {
  onUpdate?: (registration: ServiceWorkerRegistration) => void;
  onSuccess?: (registration: ServiceWorkerRegistration) => void;
}

export function register(config?: Config) {
  if (process.env.NODE_ENV === 'production' && 'serviceWorker' in navigator) {
    // Provide a fallback for PUBLIC_URL if it's undefined
    const publicUrl = new URL(
      process.env.PUBLIC_URL || '',
      window.location.href,
    );

    if (publicUrl.origin !== window.location.origin) {
      return;
    }

    window.addEventListener('load', () => {
      const swUrl = `${publicUrl}/serviceЦorker.ts`; // Ensure the correct path to the service worker

      if (isLocalhost) {
        checkValidServiceWorker(swUrl, config);

        navigator.serviceWorker.ready.then(() => {
          console.log(
            'This web app is being served cache-first by a service ' +
              'worker. To learn more, visit https://bit.ly/CRA-PWA',
          );
        });
      } else {
        registerValidSW(swUrl, config);
      }
    });
  }
}

async function registerValidSW(swUrl: string, config?: Config) {
  try {
    const registration = await navigator.serviceWorker.register(swUrl);
    registration.onupdatefound = () => {
      const installingWorker = registration.installing;
      if (installingWorker == null) {
        return;
      }
      installingWorker.onstatechange = () => {
        if (installingWorker.state === 'installed') {
          if (navigator.serviceWorker.controller) {
            console.log(
              'New content is available and will be used when all ' +
                'tabs for this page are closed. See https://bit.ly/CRA-PWA.',
            );

            if (config && config.onUpdate) {
              config.onUpdate(registration);
            }
          } else {
            console.log('Content is cached for offline use.');

            if (config && config.onSuccess) {
              config.onSuccess(registration);
            }
          }
        }
      };
    };
  } catch (error) {
    console.error('Error during service worker registration:', error);
  }
}

async function checkValidServiceWorker(swUrl: string, config?: Config) {
  try {
    const response = await fetch(swUrl, {
      headers: { 'Service-Worker': 'script' },
    });

    const contentType = response.headers.get('content-type');
    if (
      response.status === 404 ||
      (contentType != null && contentType.indexOf('javascript') === -1)
    ) {
      const registration = await navigator.serviceWorker.ready;
      await registration.unregister();
      window.location.reload();
    } else {
      registerValidSW(swUrl, config);
    }
  } catch {
    console.log(
      'No internet connection found. App is running in offline mode.',
    );
  }
}

export function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.unregister();
    });
  }
}
