# Authentication

This document provides a comprehensive guide to implementing authentication in Flet applications using OAuth 2.0.

Here are the key takeaways:

*   **OAuth 2.0 Support**: Flet supports authentication using any 3rd-party identity provider that uses the OAuth 2.0 Authorization Code Flow. Built-in providers include GitHub, Google, Azure, and Auth0. You can also configure a custom OAuth provider.
*   **Login Process**: The authentication process involves redirecting the user to the provider's website to sign in and grant consent. Flet then exchanges the authorization code for an access token.
*   **Configuration**: To get started, you need to register an OAuth app with your chosen provider to get a "Client ID" and "Client secret". The authorization callback URL should be in the format `{application-url}/oauth_callback`.
*   **Implementation**: The `page.login(provider)` method initiates the authentication flow. The `page.on_login` event handler is called upon completion, and user details can be accessed from `page.auth.user`.
*   **Token Management**: The access token is available via `page.auth.token.access_token` and can be used to make API requests to the provider. Flet automatically refreshes the token when it expires. For persistent logins ("Remember me"), the token can be encrypted and stored in `page.client_storage`.
*   **Security**: The documentation strongly advises against embedding secrets like client IDs and secrets directly in the source code. Instead, it recommends using environment variables. It also provides guidance on encrypting sensitive data before storing it.
*   **Customization**: The authentication flow can be customized. For example, you can change the content of the "Authorization complete" page or open the authorization page in the same browser tab.
