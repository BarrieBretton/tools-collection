import os, PyPDF2

#Ask user where the PDFs are
userpdflocation=input('Folder path to PDFs that need merging: ')

#Sets the scripts working directory to the location of the PDFs
os.chdir(userpdflocation)

#Ask user for the name to save the file as
userfilename=input('What should I call the file? ')

#Get all the PDF filenames
pdf2merge = [i for i in os.listdir('.') if i.endswith('.pdf')]

inv_order = 0
while True:
    print("\n")
    for i, j in enumerate(pdf2merge):
        print(f"  [{i+1}]: {j}")
    print()
    
    if (inv_order == 0):
        order = input("Press [ENTER] to continue with this order\n  else type desired order of indices separated by spaces: ").strip()
    else:
        order = input("Type a valid order of indices separated by spaces: ").strip()
        inv_order = 0

    if (order != ''):
        if all([x.isnumeric() for x in order.split()]):
            pdf2merge = [pdf2merge[int(i)-1] for i in order.split()]
        else:
            print("Invalid order, retry")
            inv_order = 1
    
    else:
        print("PDF Merger complete")
        break

pdfWriter = PyPDF2.PdfFileWriter()

#loop through all PDFs
for filename in pdf2merge:
#rb for read binary
    pdfFileObj = open(filename,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
#Opening each page of the PDF
    for pageNum in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(pageNum)
        pdfWriter.addPage(pageObj)
#save PDF to file, wb for write binary
pdfOutput = open(userfilename+'.pdf', 'wb')
#Outputting the PDF
pdfWriter.write(pdfOutput)
#Closing the PDF writer
pdfOutput.close()

