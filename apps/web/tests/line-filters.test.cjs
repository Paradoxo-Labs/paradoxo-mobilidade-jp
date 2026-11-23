const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const context={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../line-filters.js'),'utf8'),context);
const filters=context.window.ProposalFilters;
const places={cristo:{label:'Cristo',kind:'terminal'},metro:{label:'Varadouro',terminal:true},lagoa:{label:'Terminal da Lagoa',kind:'terminal'},station:{label:'Estação',kind:'station'},old:{label:'Arquivado',kind:'terminal',archived:true}};
const describe=l=>JSON.parse(JSON.stringify(filters.describe(l,places)));
test('corredor viário e família numérica são independentes',()=>{
 const line={code:'T-410',points:['pedro'],sentidos:[]};
 assert.equal(describe(line).family,'4');assert.deepEqual(describe(line).corridors,['3']);
 assert.equal(filters.matches(line,places,{corridor:'3',family:'4'}),true);
 assert.equal(filters.matches(line,places,{corridor:'4',family:'4'}),false);
});
test('as vias registradas reconhecem acentos e variantes do mesmo eixo',()=>{
 const line={code:'L-999',sentidos:[{street_sequence:['Avenida José Américo de Almeida','Avenida Presidente Epitácio Pessoa','Rodovia BR-230']}]};
 assert.deepEqual(describe(line).corridors,['4','5','8']);
});
test('nomes semelhantes não atribuem outro corredor',()=>{
 const line={code:'R-241',points:['jose_americo'],sentidos:[{street_sequence:['Praça Pedro Américo','Rua Hortêncio Osterne Carneiro']}]};
 assert.deepEqual(describe(line).corridors,[]);
});
test('terminais incluem origem, destino, vínculos intermediários e referências legadas da Lagoa',()=>{
 const line={code:'BRS-100',points:['cristo'],sentidos:[{waypoints:['lagoa_ida','lagoa_volta'],station_ids:['metro','station','old'],control_points:[{station_id:'cristo'}]}]};
 assert.deepEqual(describe(line).terminals,['cristo','lagoa','metro']);
});
test('um ponto não vinculado não vira terminal pela proximidade',()=>{
 assert.deepEqual(describe({code:'L-251',points:['rangel']}).terminals,[]);
 assert.equal(filters.matches({code:'L-251',points:['rangel']},places,{terminal:'cristo'}),false);
});
test('combinação de corredor, família e terminal usa interseção',()=>{
 const line={code:'L-251',points:['rangel','cristo']};
 assert.equal(filters.matches(line,places,{corridor:'2',family:'2',terminal:'cristo'}),true);
 assert.equal(filters.matches(line,places,{corridor:'2',family:'5',terminal:'cristo'}),false);
 assert.equal(filters.matches(line,places,{corridor:'2',family:'2',terminal:'metro'}),false);
});
test('rascunhos sem numeração ou associação podem ser encontrados',()=>{
 const line={code:'',points:[]};
 assert.equal(filters.matches(line,places,{corridor:'none',family:'none',terminal:'none'}),true);
 assert.equal(describe({code:'I-015'}).family,'0');
 assert.equal(describe({code:'I-1234'}).family,'12');
});
test('consultar os filtros não modifica o cadastro',()=>{
 const line={code:'BRS-300',points:['pedro','metro'],sentidos:[]},before=JSON.stringify({line,places});
 filters.describe(line,places);filters.matches(line,places,{corridor:'3'});
 assert.equal(JSON.stringify({line,places}),before);
});
