# PDF Preview Test

Testing embedded PDF preview with a real publication.

## Method 1: iframe

<iframe src="../publications/20240408 NPS ARS 2024/20240403 NPS ARS Paper.pdf" width="100%" height="800px" style="border: 1px solid #ccc; border-radius: 8px;"></iframe>

## Method 2: object tag

<object data="../publications/20240408 NPS ARS 2024/20240403 NPS ARS Paper.pdf" type="application/pdf" width="100%" height="800px">
  <p>Your browser does not support PDF preview. <a href="20240408 NPS ARS 2024/20240403 NPS ARS Paper.pdf">Download the PDF</a>.</p>
</object>

## Method 3: iframe with relative path (no ../publications prefix)

<iframe src="20240408 NPS ARS 2024/20240403 NPS ARS Paper.pdf" width="100%" height="800px" style="border: 1px solid #ccc; border-radius: 8px;"></iframe>

## Method 4: embed tag

<embed src="20240408 NPS ARS 2024/20240403 NPS ARS Paper.pdf" type="application/pdf" width="100%" height="800px" />
