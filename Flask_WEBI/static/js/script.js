// Btn pour show le bloc recherche 

const btnsResearch = document.querySelectorAll(".btnresearch");
const blockresearchid = document.getElementById("blockresearchid");
const btnechap = document.getElementById("btnechap");

btnsResearch.forEach(btn => {
  btn.addEventListener("click", () => {
    blockresearchid.style.display = "block";
  });
});

btnechap.addEventListener("click", () => {
  blockresearchid.style.display = "none";
})



// --- Aside mobile ---
// querySelectorAll cible TOUS les éléments avec cette classe
const btnsAside = document.querySelectorAll(".btnaside");
const showAside = document.getElementById("sidebarmobile");
const btneexit = document.getElementById("btneexit");

btnsAside.forEach(btn => {
  btn.addEventListener("click", () => {
    showAside.style.display = "block";
  });
});

btneexit.addEventListener("click", () => {
  showAside.style.display = "none";
});