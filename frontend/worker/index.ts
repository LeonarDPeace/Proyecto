/// <reference lib="webworker" />

declare const self: ServiceWorkerGlobalScope;

// Escuchar eventos de Push enviados por el backend (pywebpush)
self.addEventListener("push", (event) => {
  const data = event.data?.json() || { 
    title: "VeraMarket", 
    body: "Tienes una nueva notificación." 
  };

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/icons/icon-192x192.png",
      badge: "/icons/icon-192x192.png",
      data: data.url || "/",
    })
  );
});

// Comportamiento al hacer clic en la notificación
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: "window" }).then((clientList) => {
      // Si la app ya está abierta, enfocamos esa pestaña
      for (const client of clientList) {
        if (client.url === event.notification.data && 'focus' in client) {
          return client.focus();
        }
      }
      // De lo contrario abrimos una nueva
      if (self.clients.openWindow) {
        return self.clients.openWindow(event.notification.data);
      }
    })
  );
});
