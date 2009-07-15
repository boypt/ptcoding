import java.net.*;
import java.io.*;

public class CETQuery {
	public static void main(String[] args) {
			
		if ((args.length != 2) || ((args[0] == "4") || (args[1] == "6"))
				|| (args[1].length() != 15)) {
			System.out.println("Error: 程序参数错误，考试类型（4、6），准考证号长度（15位）");
			System.out.println("\nExample:\n\njava CETQuery 4 123456789012345\n\n");
			System.out.println("CETQuery-Java version 0.1  2009.2.26\n\n    An Exercise Program by PT, GZ University\n    Author Blog: http://apt-blog.co.cc , Welcome to Drop by.\n\n");
			System.exit(1);
		}

		String cet_url = "http://cet.99sushe.com/cetscore_99sushe0902.html?t="
				+ args[0] + "&id=" + args[1];
		String result = new String();

		try {
			URL url = new URL(cet_url);
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.addRequestProperty("Referer", "http://cet.99sushe.com/");
			// conn.setRequestMethod("POST");
			System.out.println("Connectting....\n" + conn.getURL());
			InputStream in = conn.getInputStream();
			byte[] data = new byte[1024];
			while (in.read(data) > 0) {
				result += new String(data, "gb2312");
			}
			in.close();
		} catch (Exception e) {
			System.out.println(e);
		}

	    System.out.println(result);

		String[] array = result.split(",");
		String[] type = { "听力", "阅读", "综合", "写作", "总分", "学校", "姓名", "Prev 1",
				"Next 1", "Next 2" };
		System.out.printf("\n***** CET %s 成绩清单 *****\n", args[0]);
		System.out.println("-准考证号: " + args[1]);
		for (int i = 0; i < array.length; i++) {
			System.out.printf("-%s: %s\n", type[i], array[i]);
		}
		System.out.println("**************************\n");
	}
}
