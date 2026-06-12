import AsyncStorage from "@react-native-async-storage/async-storage";

const KEY = "@label_manager:selected_printer_id";

export async function saveSelectedPrinterId(id: string): Promise<void> {
  await AsyncStorage.setItem(KEY, id);
}

export async function loadSelectedPrinterId(): Promise<string | null> {
  return AsyncStorage.getItem(KEY);
}

export async function clearSelectedPrinterId(): Promise<void> {
  await AsyncStorage.removeItem(KEY);
}
