package mk.ukim.finki.stockmap.utils;

import java.io.*;

public class PythonExecutor {

    public void executePythonScript() {
        try {
            Process process = new ProcessBuilder("python", "./stockMap.py").start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }
            process.waitFor();
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}
