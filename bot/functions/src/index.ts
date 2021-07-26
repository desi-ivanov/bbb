import * as functions from "firebase-functions";
import fetch from "node-fetch";
import dotenv = require("dotenv");
dotenv.config();

const TG_BOT_KEY = process.env["TG_BOT_KEY"]!;
const LAMBDA_KEY = process.env["LAMBDA_KEY"]!;

export const bbb_render = functions.https.onRequest((request, response) => {

  const body: TGBody = request.body;
  if(body.message && body.message.text) {
    if(body.message.text.startsWith("/start")) {
      sendMessage(body.message.chat.id, "Welcome to BBB Renderer Bot. Use the command /render url to create a video out of a BBB recording. Example usage:\n/render https://bbb-cluster.example.it/playback/presentation/2.0/playback.html?meetingId=xxxxxxxxxxxxxxxxxxxxxxxxxx")
    } else if(body.message.text.startsWith("/render")) {
      const [_, bbb_url, mbyfps] = body.message.text.split(" ");

      const url = new URL(bbb_url);
      const origin = url.origin;
      const meetingId = new URLSearchParams(url.search).get("meetingId");
      const fps = mbyfps && !isNaN(parseInt(mbyfps)) && parseInt(mbyfps) < 10 ? mbyfps : 3;

      fetch(
        "https://yumsmc7ndj.execute-api.eu-central-1.amazonaws.com/default/function"
        , {
          method: "POST"
          , headers: { "x-api-key": LAMBDA_KEY }
          , body: JSON.stringify(
            {
              "origin": origin,
              "meeting_id": meetingId,
              "fps": fps + "",
              "chat_id": body.message.chat.id
            })
        }
      ).catch(console.error)
      sendMessage(body.message.chat.id, "Rendering started. I will send you a link once it's ready").catch(console.error);
    } else {
      sendMessage(body.message.chat.id, "Unknown command").catch(console.error);
    }
  }
  response.send("ok");
});

export function sendMessage(chat_id: string | number, text: string) {
  return fetch(`https://api.telegram.org/bot${TG_BOT_KEY}/sendMessage?chat_id=${chat_id}&text=${encodeURIComponent(text)}`);
}

type TGBody = {
  update_id: number
  message: {
    message_id: number
    from: {
      id: number
      is_bot: boolean
      first_name: string
      last_name: string
      username: string
      language_code: string
    }
    chat: {
      id: number
      first_name: string
      last_name: string
      username: string
      type: string
    }
    date: number
    text: string
  }
}