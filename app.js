var restify = require('restify');
const express = require('express');

const expport = 8080;
const restport = expport + 1;

const sqlite3 = require('sqlite3').verbose();
let db = new sqlite3.Database('./db/rally-dump.sqlite3', sqlite3.OPEN_READONLY, (err) => {
	if (err) {
		return console.error(err.message);
	}
	console.log('Connected to the database');
});

function closeDb() {
	db.close((err) => {
		if (err) {
			return console.error(err.message);
		}
		console.log('Closing the database');
	});
}

function printReport_http(req, res) {
	owners = [];
	db.serialize(function() {
		db.each('select us.owner, features.priority, count(*) as count from US inner join features on us.Feature = features."Formatted ID" where us.release="IME 1.3" group by us.owner, features.priority', function (err, rows) {
			// First get the list of owner names
			for (let row in rows) {
				// console.log(row, rows[row]);
				if (not rows.Owner in owners) {
					owners.unshift(rows.Owner);
					console.log('adding %s', rows.Owner);
				}
			}
		}, function() {
			console.log(owners);
			console.log('2');
			res.json(owners);
		});
	});
}

function printReport_rest(req, res, next) {
	db.all('select us.owner, features.priority, count(*) as count from US inner join features on us.Feature = features."Formatted ID" where us.release="IME 1.3" group by us.owner, features.priority', function (err, rows) {
		res.send(rows);
	});
	next();
}

function respondTest_rest(req, res, next) {
  res.send({'hello ': req.params.name});
  next();
}

var restserver = restify.createServer();
restserver.get('/', printReport_rest);
restserver.get('/hello/:name', respondTest_rest);
restserver.head('/hello/:name', respondTest_rest);

const expserver = express();
expserver.get('/', printReport_http);

process.on('SIGTERM', function () {
	console.log("Closing via SIGTERM");
	closeDb();
	process.exit(0);
});

process.on('SIGSTOP', function () {
	console.log("Closing via SIGSTOP");
	closeDb();
	process.exit(0);
});

process.on('SIGINT', function () {
	console.log("Closing via SIGINT");
	closeDb();
	process.exit(0);
});

restserver.listen(restport, function() {
  console.log('%s listening at %s (process: %s)', restserver.name, restserver.url, process.pid);
});

expserver.listen(expport, () => console.log(`HTTPServer listening on port ${expport}`));
