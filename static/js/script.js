const btnresearch = document.getElementById("btnresearch");
const blockresearchid = document.getElementById("blockresearchid");

const btnechap = document.getElementById("btnechap");

btnresearch.addEventListener("click", () => {
  blockresearchid.style.display = "block";
});

btnechap.addEventListener("click", () => {
  blockresearchid.style.display = "none";
})