import java.util.Random;

/**
 * @author wendi
 */
public class Solution {
	
	final int MAX_ATTEMPTS = 100;
	
	/**
	 * generate grid
	 * @param int size
	 * @param int boatNum
	 * @return int[][] grid
	 */
	public int[][] generateGrid(int size, int boatNum) {
		if (size < 3 || boatNum == 0) {
			throw new RuntimeException("Bad input! Minimum grid size is 3. Minimum boatNum is 1.");
		}
		if (size * size / 3 < boatNum) {
			throw new RuntimeException(
					String.format("Bad input! Maximum boatNum in %dx%d grid is %d",
					size, size, size * size / 3));
		}
		System.out.printf("Generating %dx%d grid with %d boats.\n", size, size, boatNum);
		// generate grid without boat
		int[][] grid = new int[size][size];
		for (int i = 0; i < size - 1; i++) {
			for (int j = 0; j < size - 1; j++) {
				grid[i][j] = 0;
			}
		}
		
		// input boat
		Random rand = new Random();
		int currBoatNum = 0;
		for (int attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {			
			int x = rand.nextInt(size);
			int y = rand.nextInt(size);
			if (rand.nextInt(2) == 0) {      // horizontal
				if (x == 0 || x == size - 1 ||
					grid[x - 1][y] != 0 || grid[x][y] != 0 || grid[x + 1][y] != 0) {
					continue;
				}
				currBoatNum++;
				grid[x - 1][y] = currBoatNum;
				grid[x][y] = currBoatNum;
				grid[x + 1][y] = currBoatNum;
			}
			else {                           // vertical
				if (y == 0 || y == size - 1 ||
					grid[x][y - 1] != 0 || grid[x][y] != 0 || grid[x][y + 1] != 0) {
					continue;
				}
				currBoatNum++;
				grid[x][y - 1] = currBoatNum;
				grid[x][y] = currBoatNum;
				grid[x][y + 1] = currBoatNum;
			}
			if (currBoatNum == boatNum) {
				System.out.printf("Successful in %d attempts.\n\n", attempt);
				break;
			}
		}

		if (currBoatNum != boatNum) {
			System.out.printf("Failed in %d attempts.\n\n", MAX_ATTEMPTS);
		}
		
		return grid;
	}
	
	/**
	 * print Grid
	 * @param int[][] grid
	 */
	public void printGrid(int[][] grid) {
		if (grid.length == 0 || grid[0].length == 0) {
			throw new RuntimeException("Bad grid. Grid size should be larger than 0.");
		}
		for (int i = 0; i < grid.length; i++) {
			for (int j = 0; j < grid[0].length; j++) {
				System.out.printf("%2d ", grid[i][j]);
			}
			System.out.println();
		}
	}

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Solution sol = new Solution();
		int[][] grid = sol.generateGrid(4, 5);
		sol.printGrid(grid);
	}

}
