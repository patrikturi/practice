import {
  AuthenticationDetails,
  CognitoUser,
  CognitoUserAttribute,
  CognitoUserPool,
} from 'amazon-cognito-identity-js';
import { config } from './config';

function pool() {
  return new CognitoUserPool({
    UserPoolId: config.userPoolId,
    ClientId: config.clientId,
  });
}

export function getCurrentUser() {
  return pool().getCurrentUser();
}

export function getSession() {
  const user = getCurrentUser();
  if (!user) return Promise.resolve(null);
  return new Promise((resolve, reject) => {
    user.getSession((err, session) => {
      if (err) return reject(err);
      if (!session?.isValid()) return resolve(null);
      resolve(session);
    });
  });
}

export async function getAccessToken() {
  const session = await getSession();
  return session?.getAccessToken()?.getJwtToken() || null;
}

export function signIn(email, password) {
  const user = new CognitoUser({ Username: email, Pool: pool() });
  const details = new AuthenticationDetails({ Username: email, Password: password });
  return new Promise((resolve, reject) => {
    user.authenticateUser(details, {
      onSuccess: (session) => resolve(session),
      onFailure: reject,
      newPasswordRequired: () => reject(new Error('New password required; complete in Cognito console for now.')),
    });
  });
}

export function signUp(email, password) {
  return new Promise((resolve, reject) => {
    pool().signUp(
      email,
      password,
      [new CognitoUserAttribute({ Name: 'email', Value: email })],
      null,
      (err, result) => (err ? reject(err) : resolve(result))
    );
  });
}

export function confirmSignUp(email, code) {
  const user = new CognitoUser({ Username: email, Pool: pool() });
  return new Promise((resolve, reject) => {
    user.confirmRegistration(code, true, (err, result) => (err ? reject(err) : resolve(result)));
  });
}

export function signOut() {
  getCurrentUser()?.signOut();
}
