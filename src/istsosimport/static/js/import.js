PetiteVue.createApp({
  $delimiters: ["${", "}"],
  currentService: null,
  procedures: [],
  fetchProcedure() {
    if (this.currentService) {
      fetch("api/" + this.currentService + "/procedures")
        .then((r) => r.json())
        .then((r) => (this.procedures = r));
    } else {
      this.procedures = [];
    }
  },
}).mount("#app");
