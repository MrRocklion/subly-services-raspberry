// Ejecuta al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  const bar = document.getElementById("progress-bar");

  // Comienza el proceso de actualización en segundo plano
  fetch('/start-update');

  // Actualiza la barra cada 500ms
  const interval = setInterval(() => {
    fetch('/progress')
      .then(res => res.json())
      .then(data => {
        bar.style.width = data.progress + "%";
        if (data.progress >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            window.location.href = "/";
          }, 1000);
        }
      });
  }, 500);
});
