findClosestPeriod = function (raoSchema, wavePeriod) {
	let minDiff = Infinity;
	let modelScale = 70;
	let periodCandidate;
	for (let prop in raoSchema["surge"]) {
		let schemaPeriod = parseFloat(prop);
		if (typeof periodCandidate === "undefined") {
			periodCandidate = schemaPeriod;
		}
		let periodScaled = schemaPeriod / Math.sqrt(modelScale);
		let diffCurr = Math.abs(wavePeriod - periodScaled);
		if (Math.abs(diffCurr) < Math.abs(minDiff)) {
			periodCandidate = schemaPeriod;
			minDiff = diffCurr;
		}
	}
	return periodCandidate;
};
