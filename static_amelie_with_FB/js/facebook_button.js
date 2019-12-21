
FB.getLoginStatus(function(response) {
  if (response.status === 'connected') {
    // The user is logged in and has authenticated your
    // app, and response.authResponse supplies
    // the user's ID, a valid access token, a signed
    // request, and the time the access token
    // and signed request each expire.
    var uid = response.authResponse.userID;
    var accessToken = response.authResponse.accessToken;
  } else if (response.status === 'authorization_expired') {
    // The user has signed into your application with
    // Facebook Login but must go through the login flow
    // again to renew data authorization. You might remind
    // the user they've used Facebook, or hide other options
    // to avoid duplicate account creation, but you should
    // collect a user gesture (e.g. click/touch) to launch the
    // login dialog so popup blocking is not triggered.
  } else if (response.status === 'not_authorized') {
    // The user hasn't authorized your application.  They
    // must click the Login button, or you must call FB.login
    // in response to a user gesture, to launch a login dialog.
  } else {
    // The user isn't logged in to Facebook. You can launch a
    // login dialog with a user gesture, but the user may have
    // to log in to Facebook before authorizing your application.
  }
 });

FB.api('/me', function(response) {
    console.log(JSON.stringify(response));
});