const btnresearch = document.getElementById("btnresearch");
const blockresearchid = document.getElementById("blockresearchid");

const btnechap = document.getElementById("btnechap");

btnresearch.addEventListener("click", () => {
  blockresearchid.style.display = "block";
});

btnechap.addEventListener("click", () => {
  blockresearchid.style.display = "none";
})


const blockquestion1 = document.getElementById("QCM1id");
const btnext = document.getElementById("Q2");

btnext.addEventListener("click", () => {
  blockquestion1.style.display = "none";
}); 