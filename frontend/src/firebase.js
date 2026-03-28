// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDDOfhDUw0M55hxsB2AqHTJ9lu9hYmkQYY",
  authDomain: "f1rechat-3c9b4.firebaseapp.com",
  projectId: "f1rechat-3c9b4",
  storageBucket: "f1rechat-3c9b4.firebasestorage.app",
  messagingSenderId: "883732998953",
  appId: "1:883732998953:web:9b39f05d3b0f6f57bf6538",
  measurementId: "G-103GQK5BNK"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
