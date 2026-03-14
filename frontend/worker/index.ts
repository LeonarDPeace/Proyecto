/// <reference lib="webworker" />

export {};
declare const self: ServiceWorkerGlobalScope;

// Escuchar eventos de Push enviados por el backend (pywebpush)
self.addEventListener("push", (event) => {
  let data = { 
    title: "VeraMarket", 
    body: "Tienes una nueva notificación." 
  };

  try {
    if (event.data) {
      data = event.data.json();
    }
  } catch (e) {
    // Si no es JSON, intentar como texto
    data.body = event.data?.text() || data.body;
  }

  if (Notification.permission !== "granted") {
    console.warn("Permiso de notificaciones no concedido.");
    return;
  }

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/icons/icon-192x192.png",
      badge: "/icons/icon-192x192.png",
      data: (data as any).url || "/",
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
