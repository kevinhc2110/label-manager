import { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { checkPrintersHealth, getPrinters } from "../api/labelManager";
import { loadSelectedPrinterId, saveSelectedPrinterId } from "../api/storage";
import { Printer, PrinterHealth } from "../types/printer";

const ICONS = {
  printer: "🖨️",
  online: "🟢",
  offline: "🔴",
  location: "📍",
  ip: "🌐",
};

export default function PrinterListScreen({
  navigation,
}: {
  navigation: any;
}) {
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [healthMap, setHealthMap] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const insets = useSafeAreaInsets();
  const hasAutoNavigated = useRef(false);

  const navigateToPrinter = useCallback(
    (printer: Printer) => {
      if (typeof document !== "undefined") {
        (document.activeElement as HTMLElement | null)?.blur();
      }
      navigation.navigate("PrintLabel", { printer });
    },
    [navigation]
  );

  const fetchHealth = useCallback(async () => {
    try {
      const healthData = await checkPrintersHealth();
      const map: Record<string, boolean> = {};
      for (const h of healthData) {
        map[h.printer_id] = h.is_online;
      }
      setHealthMap(map);
    } catch {
      // health check non-critical
    }
  }, []);

  const fetchPrinters = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const data = await getPrinters();
      setPrinters(data);
      return data;
    } catch {
      return [];
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchPrinters().then(async (data) => {
      if (hasAutoNavigated.current) return;
      const savedId = await loadSelectedPrinterId();
      if (!savedId) return;
      const match = data.find((p) => p.id === savedId);
      if (match) {
        hasAutoNavigated.current = true;
        if (typeof document !== "undefined") {
          (document.activeElement as HTMLElement | null)?.blur();
        }
        navigateToPrinter(match);
      }
    });
    fetchHealth();
  }, [fetchPrinters, navigateToPrinter, fetchHealth]);

  const handleSelect = async (printer: Printer) => {
    await saveSelectedPrinterId(printer.id);
    navigateToPrinter(printer);
  };

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await Promise.all([fetchPrinters(true), fetchHealth()]);
    setRefreshing(false);
  }, [fetchPrinters, fetchHealth]);

  const isOnline = (p: Printer) => {
    if (p.id in healthMap) return healthMap[p.id];
    return p.is_active;
  };

  const renderCard = ({ item }: { item: Printer }) => {
    const online = isOnline(item);
    return (
      <TouchableOpacity
        activeOpacity={0.7}
        onPress={() => handleSelect(item)}
        style={{
          backgroundColor: "#1e293b",
          borderRadius: 16,
          padding: 20,
          marginHorizontal: 16,
          marginBottom: 12,
          borderWidth: 1,
          borderColor: online ? "#22c55e33" : "#334155",
        }}
      >
        <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 12 }}>
          <Text style={{ fontSize: 28, marginRight: 12 }}>{ICONS.printer}</Text>
          <View style={{ flex: 1 }}>
            <Text style={{ color: "#f8fafc", fontSize: 18, fontWeight: "700" }}>
              {item.name}
            </Text>
            <View style={{ flexDirection: "row", alignItems: "center", marginTop: 2 }}>
              <Text style={{ fontSize: 10, marginRight: 4 }}>
                {online ? ICONS.online : ICONS.offline}
              </Text>
              <Text style={{ color: "#94a3b8", fontSize: 13 }}>
                {online ? "Online" : "Offline"}
              </Text>
            </View>
          </View>
          <Text style={{ color: "#6366f1", fontSize: 20 }}>›</Text>
        </View>

        <View style={{ flexDirection: "row", gap: 16 }}>
          <View style={{ flexDirection: "row", alignItems: "center" }}>
            <Text style={{ fontSize: 14, marginRight: 4 }}>{ICONS.location}</Text>
            <Text style={{ color: "#cbd5e1", fontSize: 13 }}>{item.location}</Text>
          </View>
          <View style={{ flexDirection: "row", alignItems: "center" }}>
            <Text style={{ fontSize: 14, marginRight: 4 }}>{ICONS.ip}</Text>
            <Text style={{ color: "#cbd5e1", fontSize: 13 }}>{item.ip_address}</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: "#0f172a",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: "#0f172a", paddingTop: insets.top }}>
      <View style={{ paddingHorizontal: 16, paddingVertical: 20 }}>
        <Text style={{ color: "#f8fafc", fontSize: 28, fontWeight: "800" }}>
          Printers
        </Text>
        <Text style={{ color: "#64748b", fontSize: 14, marginTop: 4 }}>
          {printers.length} available
        </Text>
      </View>

      <FlatList
        data={printers}
        keyExtractor={(p) => p.id}
        renderItem={renderCard}
        contentContainerStyle={{ paddingBottom: 32 }}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor="#6366f1"
            colors={["#6366f1"]}
          />
        }
        ListEmptyComponent={
          <View style={{ alignItems: "center", marginTop: 60 }}>
            <Text style={{ fontSize: 48, marginBottom: 12 }}>🖨️</Text>
            <Text style={{ color: "#94a3b8", fontSize: 16 }}>
              No printers found
            </Text>
          </View>
        }
      />
    </View>
  );
}
