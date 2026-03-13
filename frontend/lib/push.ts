/**
 * Web Push utility (HU 2.3)
 */

function urlB64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export async function subscribeToPushNotifications(token: string) {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.warn("Push no está soportado por este navegador.");
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const vapidPublicKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
    
    if (!vapidPublicKey) {
      console.warn("Falta NEXT_PUBLIC_VAPID_PUBLIC_KEY en .env");
      return false;
    }

    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlB64ToUint8Array(vapidPublicKey),
    });

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/push/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(subscription),
    });

    return response.ok;
  } catch (error) {
    console.error("Error suscribiendo a push notifications:", error);
    return false;
  }
}
