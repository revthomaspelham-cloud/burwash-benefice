/**
 * Prayer requests from the website -> email to the Rector.
 * Nothing is stored: each request is simply emailed on.
 *
 * Set up (once, signed in as the St Bartholomew's account):
 * 1. Go to https://script.google.com and click "New project".
 * 2. Delete what's there, paste in this whole file, and click Save.
 * 3. Click Deploy > New deployment. Choose type "Web app".
 *    Execute as: Me.  Who has access: Anyone.  Click Deploy and allow access.
 * 4. Copy the Web app URL (it ends in /exec) and send it to Claude,
 *    or paste it after "prayer_endpoint:" in src/settings.txt.
 */
var RECTOR_EMAIL = 'revthomaspelham@gmail.com';

function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p.website) return ok_();                       // spam trap
  var request = String(p.request || '').trim().slice(0, 5000);
  if (!request) return ok_();
  var name = String(p.name || '').trim().slice(0, 200);
  var email = String(p.email || '').trim().slice(0, 200);
  var body =
    'A prayer request from the benefice website.\n\n' +
    request + '\n\n' +
    'Name: ' + (name || '(anonymous)') + '\n' +
    'Email: ' + (email || '(none given)') + '\n\n' +
    'They agreed it will be prayed for at Thursday Communion, where names may be read out.\n' +
    'Please delete this email within a month (website privacy note).';
  var opts = { name: 'Benefice website' };
  if (/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) opts.replyTo = email;
  MailApp.sendEmail(RECTOR_EMAIL, 'Prayer request' + (name ? ' from ' + name : ''), body, opts);
  return ok_();
}

function ok_() {
  return ContentService.createTextOutput('ok');
}
