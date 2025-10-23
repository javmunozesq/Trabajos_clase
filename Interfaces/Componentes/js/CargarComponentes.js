// Carga el header
fetch('/Interfaces/Componentes/componentes/header.html')
  .then(res => res.text())
  .then(data => {
    document.getElementById('header').innerHTML = data;
  });

// Carga el footer
fetch('/Interfaces/Componentes/componentes/footer.html')
  .then(res => res.text())
  .then(data => {
    document.getElementById('footer').innerHTML = data;
  });
