// src/keycloak.ts
import Keycloak from 'keycloak-js'

let keycloak: Keycloak | null = null

export function initKeycloak(): Promise<Keycloak> {
  return new Promise((resolve, reject) => {
    if (keycloak) return resolve(keycloak)

    keycloak = new Keycloak({
      url: 'http://localhost:8081',
      realm: 'desk-booking-system',
      clientId: 'vue-app',
    })

    keycloak
      .init({
        onLoad: 'check-sso',
        checkLoginIframe: true,
        checkLoginIframeInterval: 1,
        silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
      })
      .then(() => resolve(keycloak!))
      .catch((err) => reject(err))
  })
}

export function getKeycloak(): Keycloak {
  if (!keycloak) throw new Error('Keycloak not initialized')
  return keycloak
}
