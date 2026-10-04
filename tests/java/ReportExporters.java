package com.example.reports;

import java.io.IOException;
import java.io.Writer;
import java.util.List;

interface ReportExporter {
    void export(List<ReportRow> rows, Writer out) throws IOException;
}

abstract class AbstractReportExporter implements ReportExporter {
    protected String separator() {
        return ",";
    }
}

final class CsvReportExporter extends AbstractReportExporter {
    @Override
    public void export(List<ReportRow> rows, Writer out) throws IOException {
        for (ReportRow row : rows) {
            out.write(row.name() + separator() + row.total() + "\n");
        }
    }
}

final class ReportExporterFactory {
    static ReportExporter create(String format) {
        return new CsvReportExporter();
    }
}

record ReportRow(String name, long total) {}
