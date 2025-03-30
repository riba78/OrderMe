/**
 * Social Authentication Utilities
 * 
 * This module provides utilities for social authentication integration.
 * It handles:
 * 1. Facebook SDK initialization and setup
 * 2. Google One Tap configuration
 * 3. OAuth callback handling
 * 
 * Facebook Features:
 * - SDK loading and initialization
 * - App ID configuration
 * - Login status checking
 * - Event subscription
 * 
 * Google Features:
 * - One Tap sign-in setup
 * - Credential handling
 * - Auto-prompt configuration
 * - Callback management
 * 
 * Functions:
 * - initFacebookSDK: Initialize Facebook JavaScript SDK
 * - initGoogleOneTap: Set up Google One Tap sign-in
 * - handleCredentialResponse: Process Google sign-in response
 * 
 * Environment Variables:
 * - VUE_APP_FACEBOOK_APP_ID: Facebook application ID
 * - VUE_APP_GOOGLE_CLIENT_ID: Google OAuth client ID
 */

// Get the base URL for OAuth redirects
const getBaseUrl = () => {
  const protocol = process.env.VUE_APP_PROTOCOL || 'http';
  const domain = process.env.VUE_APP_DOMAIN || 'localhost';
  const port = process.env.VUE_APP_PORT || '8080';
  
  // In production, don't include default HTTPS port
  if (protocol === 'https' && port === '443') {
    return `${protocol}://${domain}`;
  }
  // In production, don't include default HTTP port
  if (protocol === 'http' && port === '80') {
    return `${protocol}://${domain}`;
  }
  // For all other cases, include the port
  return `${protocol}://${domain}:${port}`;
};

// Facebook SDK initialization
export const initFacebookSDK = () => {
  return new Promise((resolve) => {
    // Check if SDK is already loaded
    if (window.FB) {
      resolve();
      return;
    }

    window.fbAsyncInit = function() {
      window.FB.init({
        appId: process.env.VUE_APP_FACEBOOK_APP_ID,
        cookie: true,
        xfbml: true,
        version: 'v18.0'
      });
      resolve();
    };

    // Load the Facebook SDK
    (function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "https://connect.facebook.net/en_US/sdk.js";
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
  });
};

export const loginWithFacebook = () => {
  return new Promise((resolve, reject) => {
    if (!window.FB) {
      reject(new Error('Facebook SDK not initialized'));
      return;
    }

    window.FB.login((response) => {
      if (response.authResponse) {
        // Get user info with explicit fields request
        window.FB.api('/me', { 
          fields: 'email,name',
          access_token: response.authResponse.accessToken 
        }, (userInfo) => {
          if (userInfo && !userInfo.error) {
            if (userInfo.email) {
              resolve({
                ...userInfo,
                accessToken: response.authResponse.accessToken
              });
            } else {
              reject(new Error('Email permission not granted. Please allow email access to continue.'));
            }
          } else {
            reject(new Error(userInfo?.error?.message || 'Failed to get user data'));
          }
        });
      } else {
        reject(new Error('Facebook login cancelled'));
      }
    }, {
      scope: 'email,public_profile',
      return_scopes: true,
      auth_type: 'rerequest'
    });
  });
};

// Google One Tap configuration
export const initGoogleOneTap = (callback) => {
  if (!process.env.VUE_APP_GOOGLE_CLIENT_ID) return

  window.google?.accounts.id.initialize({
    client_id: process.env.VUE_APP_GOOGLE_CLIENT_ID,
    callback: callback,
    auto_select: false,
    cancel_on_tap_outside: true
  })

  window.google?.accounts.id.prompt()
}

// Configure Google OAuth
export const googleOAuthConfig = {
  clientId: process.env.VUE_APP_GOOGLE_CLIENT_ID,
  redirectUri: `${getBaseUrl()}/auth/google/callback`,
  scope: 'email profile'
}; 