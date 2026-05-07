import 'package:flutter/material.dart';

// DESIGN: The child communication board loads images directly from ARASAAC CDN —
// no backend server required. The Needs structure is static (changes only when
// the ontology is updated) so hardcoding it in Dart avoids a network round-trip
// and allows the child flow to work offline from the server.
//
// arasaacId values match the #arasaacId annotations in maths.owl.
// If you add a new Need to the ontology, update _kNeeds here as well.

// ---- Static Needs data (from maths.owl annotations) -----------------------

typedef NeedItem = ({String label, int arasaacId});

const List<NeedItem> _kPhysical = [
  (label: "J'ai faim",  arasaacId: 35559),
  (label: "J'ai soif",  arasaacId: 7273),
  (label: "Toilettes",  arasaacId: 5921),
  (label: "J'ai mal",   arasaacId: 30620),
  (label: "Pause",      arasaacId: 27339),
];

const List<NeedItem> _kMental = [
  (label: "Fatigué",       arasaacId: 35537),
  (label: "Trop de bruit", arasaacId: 7157),
];

const List<NeedItem> _kHelpValidation = [
  (label: "J'ai compris",        arasaacId: 11697),
  (label: "Je ne comprends pas", arasaacId: 37827),
  (label: "J'ai fini",           arasaacId: 5358),
  (label: "C'est bien ?",        arasaacId: 5397),
];

// ARASAAC public CDN — no server needed for images
String _pictoUrl(int arasaacId) =>
    'https://static.arasaac.org/pictograms/$arasaacId/${arasaacId}_500.png';

// ---- Screen ----------------------------------------------------------------

class ChildScreen extends StatelessWidget {
  const ChildScreen({Key? key}) : super(key: key);

  void _showPictogramDialog(BuildContext context, NeedItem item) {
    showDialog(
      context: context,
      builder: (_) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Image.network(
                _pictoUrl(item.arasaacId),
                width: 220,
                height: 220,
                fit: BoxFit.contain,
                errorBuilder: (_, __, ___) =>
                    const Icon(Icons.broken_image, size: 120, color: Colors.grey),
              ),
              const SizedBox(height: 16),
              Text(
                item.label,
                style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => Navigator.of(context).pop(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                ),
                child: const Text('Fermer', style: TextStyle(fontSize: 18)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCard(BuildContext context, NeedItem item) {
    return GestureDetector(
      onTap: () => _showPictogramDialog(context, item),
      child: Card(
        elevation: 3,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Padding(
          padding: const EdgeInsets.all(8),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Expanded(
                child: Image.network(
                  _pictoUrl(item.arasaacId),
                  fit: BoxFit.contain,
                  loadingBuilder: (_, child, progress) => progress == null
                      ? child
                      : const Center(child: CircularProgressIndicator(strokeWidth: 2)),
                  errorBuilder: (_, __, ___) =>
                      const Icon(Icons.broken_image, size: 50, color: Colors.grey),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                item.label,
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSection(
    BuildContext context,
    String title,
    Color color,
    List<NeedItem> items,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 16, 12, 8),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: color.withOpacity(0.4)),
            ),
            child: Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color.withOpacity(0.9),
              ),
            ),
          ),
        ),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 8),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            childAspectRatio: 0.85,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
          ),
          itemCount: items.length,
          itemBuilder: (ctx, i) => _buildCard(ctx, items[i]),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Je communique'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 1,
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSection(context, "J'ai besoin de...", Colors.orange, _kPhysical),
            _buildSection(context, "Je me sens...", Colors.purple, _kMental),
            _buildSection(context, "Pour le travail", Colors.teal, _kHelpValidation),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
