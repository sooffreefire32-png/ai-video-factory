const { google } = require("googleapis");

const oauth2Client = new google.auth.OAuth2(
  process.env.CLIENT_ID,
  process.env.CLIENT_SECRET,
  "urn:ietf:wg:oauth:2.0:oob"
);

// Generate login URL
const url = oauth2Client.generateAuthUrl({
  access_type: "offline",
  prompt: "consent",
  scope: ["https://www.googleapis.com/auth/youtube.upload"],
});

console.log("\n==============================");
console.log("👉 OPEN THIS LINK:");
console.log(url);
console.log("==============================\n");

console.log("After login, copy the AUTH CODE and we will exchange it for token (next step).");