var raoReq = new XMLHttpRequest();
raoReq.open("GET", "../database/seakeeping/results.txt", true);
raoReq.addEventListener("load", function (event) {
	output = event.target.response;
	useRAO(output);
});
raoReq.send(null);

var lin = [];
var rao;
var pha;
var res;
var schema = {};

var useRAO = function (result) {
	var index = 0;
	res = result.split(/[\s]+/).join(' ')
	var res2 = res.substring(1)
	var mat = res2.split(" ");
	for (i = 0; i < mat.length; i++) {
		mat[i] = +mat[i]
	}
	for (i = 0; i < mat.length / 7; i++) {
		lin[i] = mat.slice(index, index + 5)
		index = index + 7;
	}
	rao = [];
	pha = [];
	var dofs = ["surge", "sway", "heave", "roll", "pitch", "yaw"];
	var periods = [
		"628.319", "125.664", "62.8319", "41.8879", "35.9039", "31.4159", "27.9253", "25.1327", "22.8479", "20.944",
		"19.3329", "17.952", "16.7552", "15.708", "14.784", "13.9626", "13.2278", "12.5664", "11.968", "11.424",
		"10.9273", "10.472", "10.0531", "9.66644", "9.30842", "8.97598", "8.66646", "8.37758", "8.10734", "7.85398",
		"7.61598", "7.39198", "7.18078", "6.98132", "6.79263", "6.61388", "6.44429", "6.28319", "6.12994", "5.98399",
		"5.84482", "5.71199", "5.58505", "5.46364", "5.34739", "5.23599", "5.12913", "5.02655", "4.92799", "4.83322",
		"4.74203", "4.65421", "4.56959", "4.48799", "4.40925", "4.33323", "4.25979", "4.18879", "4.12012", "4.05367"
	];
	var headings = [
		"0", "15", "30", "45", "60", "75", "90", "105", "120", "135",
		"150", "165", "180", "195", "210", "225", "240", "255", "270", "285",
		"300", "315", "330", "345", "360"
	];
	var dof = dofs.length; // DoF
	var per = periods.length; // Number of periods
	var hea = headings.length; // Number of headings
	// allocate vector
	for (i = 0; i < dof; i++) {
		rao[i] = [];
		pha[i] = [];
		schema[dofs[i]] = {};
		for (j = 0; j < per; j++) {
			rao[i][j] = [];
			pha[i][j] = [];
			schema[dofs[i]][periods[j]] = {};
			for (k = 0; k < hea; k++) {
				rao[i][j][k] = [];
				pha[i][j][k] = [];
				schema[dofs[i]][periods[j]][headings[k]] = {};
			}
		}
	}
	var i, j, k, l;
	for (l = 0; l < lin.length - 1; l++) {
		i = l % dof;
		j = Math.floor(l / (dof * hea));
		k = Math.floor(l / dof) % hea;
		rao[i][j][k] = lin[l][3];
		pha[i][j][k] = lin[l][4];
		schema[dofs[i]][periods[j]][headings[k]].rao = lin[l][3];
		schema[dofs[i]][periods[j]][headings[k]].phase = lin[l][4];
		//console.log(i,j,k);
	}
}