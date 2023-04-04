import axios from "axios";

const BASE_URL = "https://5000-rameshnayak1-serviceapp-1vxj32g9d4s.ws-us93.gitpod.io"; // Change this to your Flask server's URL

export const hello = async () => {
  try {
    const response = await axios.get(`${BASE_URL}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
};
