import { useState } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router";
import type { User } from "./api-client/models/User";
import Home from "./home.tsx";
import GridView from "./images/gridView.tsx";
import UploadForm from "./images/uploadForm.tsx";

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  return (
    <Routes>
      <Route
        path="/"
        element={
          <Home currentUser={currentUser} setCurrentUser={setCurrentUser} />
        }
      />
      <Route
        path="/images"
        element={<GridView currentUser={currentUser} />}
      />
      <Route
        path="/image-upload"
        element={<UploadForm currentUser={currentUser} />}
      />
      <Route
        path="*"
        element={
          <Home currentUser={currentUser} setCurrentUser={setCurrentUser} />
        }
      />
    </Routes>
  );
}

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
);
