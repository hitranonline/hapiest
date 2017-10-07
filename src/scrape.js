// This is a utility function that can be used to scrape data about molecules from http://hitran.org/lbl/
// There aren't constants defined in HAPI about the the min or max wn, so we have to get it ourselves

str = ''
x = function() {
  $('.selectable-row').each(function(i) {
    str += this.cells[0].textContent.trim() + '    :    (' + this.cells[5].textContent.trim() + ', ' + this.cells[6].textContent.trim() + '),\n    ';
  })
}
x()
console.log(str)
