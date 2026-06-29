# IHE RAD MADO – Volume 2 – Transactions

<!-- Source: .cache/IHE_RAD_Suppl_MADO.pdf pages 32–38 -->


<!-- page 32 -->

<!-- figure: page 32 -->

______________________________________________________________________________


<a id="volume-2-transactions"></a>
# Volume 2 – Transactions

Update Section 4.107 in Volume 2. Editor Note: 4.1xy of the Public Comment version was removed and replaced by reuse of 4.107 845 with profile specific requirement clarifications as shown below. [Current 4.107.4 Messages from IHE RAD TF-2: 4.107 WADO-RS Retrieve [RAD-107]:]


<a id="41074-messages"></a>
#### 4.107.4 Messages

850


**Figure 4.107.4-1: Interaction Diagram**


<a id="410740-message-support-requirements"></a>
#### 4.107.4.0 Message Support Requirements

This transaction defines four request/response message pairs: 855 • Get Instances (Section 4.107.4.1 and 4.107.4.2) • Get Metadata (Section 4.107.4.3 and 4.107.4.4)


<!-- page 33 -->

______________________________________________________________________________ • Get Bulkdata (Section 4.107.4.5 and 4.107.4.6) • Get Rendered Instances (Section 4.107.4.7 and 4.107.4.8) A Requester shall support at least one of these request/response pairs; a Responder shall 860 support all four pairs, as defined in DICOM. Add the following new subsections


<a id="4107401-cross-enterprise-document-sharing-for-imaging-xds-ib-profile"></a>
#### 4.107.4.0.1 Cross-Enterprise Document Sharing for Imaging (XDS-I.b) Profile

A Responder in the XDS-I.b Profile shall support all four message pairs.


<a id="4107402-web-based-image-access-wia-profile"></a>
#### 4.107.4.0.2 Web-based Image Access (WIA) Profile

865 A Responder in the WIA Profile shall support all four message pairs.


<a id="4107403-integrated-multimedia-reporting-imr-profile"></a>
#### 4.107.4.0.3 Integrated Multimedia Reporting (IMR) Profile

A Responder in the IMR Profile shall support all four message pairs.


<a id="4107404-manifest-based-access-to-dicom-objects-mado-profile"></a>
#### 4.107.4.0.4 Manifest-based Access to DICOM Objects (MADO) Profile

A Responder in the MADO Profile shall support the ‘Get Instances’ message pair for Study 870 Instances, Series Instances and Instance Resources. The Responder may support the Frame Pixel Data Resource.

*Note: The Frame Pixel Data Resource is being introduced by a DICOM CP on DICOM PS3.18.*

Rendered Instances Option A Requester in the MADO Profile that claims the Rendered Instances Option shall support the 875 ‘Get Rendered Instances’ message pair for the Rendered Instance Resource. The Requester may support Rendered Series and Rendered Frame resources. A Responder in the MADO Profile that claims the Rendered Instances Option shall support the ‘Get Rendered Instances’ message pair for the Rendered Instance Resource. The Responder may support Rendered Series and Rendered Frame resources. 880 4.107.4.0.5 Cross-Community Web-Based Access to DICOM Objects (XC-WADO) Profile A Requester and a Responder in the XC-WADO Profile shall support the ‘Get Instances’ message pair as defined in DICOM PS3.18. They may optionally support the ‘Get Rendered Instances’ message pair as defined in DICOM PS3.18. 885


<!-- page 34 -->

______________________________________________________________________________ Add Appendix XA to Volume 2x appendices


<a id="appendix-xa-managing-the-addresses-of-the-sources-of-images-to"></a>
## Appendix XA – Managing the addresses of the sources of images to


<a id="retrieve-beyond-a-single-community"></a>
## retrieve beyond a single community

890 This appendix provides information about the way the addresses of image sources are handled both within a Community where the DICOM instances are accessed through the MADO Profile, as well as Cross-community where the MADO Profile is grouped with the XC-WADO Profile.

*Note: The term Community is used to consider a set of Imaging Document Sources, Content Creators and Imaging Document*

895

*Consumers that are implemented by individual organizations or enterprises. The way the MADO actors are integrated*

*within their respective individual organizations or enterprises is beyond the scope of the MADO Profile and may use*

*IHE profiles such as IHE WIA, IHE SWF.b, ARI. Examples of such Communities are regional ehealth networks, and*

*national ehealth infrastructures.*

*The term Cross-community is used to consider how one or more Communities, as defined above, may be integrated and*

900

*allow actors such as Imaging Document Consumers to access Imaging Document Sources from other Communities to*

*retrieve DICOM Instances across these Community boundaries.*

In particular, the way the WADO-RS Request conveys address information in such a mixed environment is handled. The following four figures present an example of Cross-community handling of the retrieve URL 905 used in the WADO-RS transactions. Figures XA-1 and XA-2 depict the case of a Community A that uses a Retrieve Location UID. Figures XA-3 and XA-4 depict the case of a Community A that uses a Retrieve URL in the imaging study manifest (See Section X.4.1.2 Intra-community sharing infrastructure). In these examples, a Cross-community WADO-RS Retrieve transaction initiates from a 910 Community B Imaging Document Consumer and progresses via Initiating and Responding Imaging Gateways to reach the Community A where the Imaging Document Source is located. The example focuses on the WADO-RS retrieve URL, and the value it contains, as it moves from B to A. These transformations are specified by the XC-WADO Profile using the MADO specified imaging study manifest (see Section 58.4.1.5 DICOMweb Study Service Retrieve 915 transaction URI). The elements manipulated during transactions used in Figures XA-1, XA-2, XA-3, XA-4 that provide examples of the URL transformation by the gateways where the responding community either includes or not the Retrieve URL (0008,1190) attribute into the published imaging study manifests: 920 • Initiating Imaging Gateway hostname: initiating-gateway.example.com • Initiating Imaging Gateway endpoint_path: wado • Responding Imaging Gateway hostname: responding-gateway.example.org • Responding Imaging Gateway endpoint_path: wado-rs • Initiating Community homeCommunityId: urn:oid:1.2.3.4


<!-- page 35 -->

<!-- figure: page 35 -->

______________________________________________________________________________ 925 • Responding Community homeCommunityId: urn:oid:5.6.7.8 • RetrieveLocationUID: 1.2.840.9.10.11.12 • Retrieve URL (base URI): hostname/dicom-web-rs/ • Imaging Document Source hostname: document-source.example.org 930


**Figure XA-1: Image retrieval by XC-WADO with Domain A using lookup of Retrieve**


**Location UID - Transactions**


<!-- page 36 -->

______________________________________________________________________________ 935 Given a manifest for the imaging study 1.2.840.113619.2.207.28521.42888.1640475282.450/ coming from homeCommunityID/5.6.7.8 and containing a retrieveLocationUID 1.2.840.. and no retrieve URL The Manifest is associated with homeCommunityID/5.6.7.8 which is not the Local Home CommunityID [1] The B_IDC sees a different homeCommunityID than its own and can construct the appropriate URL. https://initiating-gateway.example.com/wado/ homeCommunityId/5.6.7.8/RetrieveLocationUID/1.2.840.9.10.11.12/ study/1.2.840.113619.2.207.28521.42888.1640475282.450/ [2] B_IIGW uses A_homeCommunityID to map (lookup) the hostname for A_RGW according to local configuration in B_IGW and constructs the appropriate URL https://responding-gateway.example.org/wado-rs/ homeCommunityId/5.6.7.8/RetrieveLocationUID/1.2.840.9.10.11.12/ study/1.2.840.113619.2.207.28521.42888.1640475282.450/ [3] A_RIGW The initial string document-source.example.org/pacs/wado-rs needs to be obtained from local lookup using the retrieve location UID (OID) https://document-source.example.org/pacs/wado-rs/ study/1.2.840.113619.2.207.28521.42888.1640475282.450 [4] Domain A document source responds with multi-part encoded DICOM objects (images) as payload


**Figure XA-2: WADO-RS Retrieve URL with Domain A**


**using lookup of Retrieve Location UID – Example of related URL values**


<!-- page 37 -->

<!-- figure: page 37 -->

______________________________________________________________________________


**Figure XA-3: Image retrieval by XC-WADO with Domain A directly using the**

940


**Retrieve URL – Transaction flows**

945


<!-- page 38 -->

______________________________________________________________________________ 950 Given a manifest for imaging study 1.2.840.113619.2.207.28521.42888.1640475282.450/ coming from homeCommunityID/5.6.7.8 and containing a retrieveLocationUID 1.2.840.. and with a retrieve URL hostname/dicom-web-rs The Manifest is associated with a homeCommunityID/5.6.7.8 which is not the Local Home 955 CommunityID [1] The B_IDC sees a different homeCommunityID than its own and can construct the appropriate URL. https://initiating-gateway.example.com/wado/ homeCommunityId/5.6.7.8/RetrieveLocationUID/1.2.840.9.10.11.12/ 960 study/1.2.840.113619.2.207.28521.42888.1640475282.450 ?retrieveurl=hostname/dicom-web-rs/ [2] B_IIGW uses A_homeCommunityID to map (lookup) the hostname for A_RGW according to local configuration in B_IGW and constructs the appropriate URL https://responding-gateway.example.org/wado-rs/ homeCommunityId/5.6.7.8/RetrieveLocationUID/1.2.840.9.10.11.12/ 965 study/1.2.840.113619.2.207.28521.42888.1640475282.450 ?retrieveurl=hostname/dicom-web-rs/ [3] A_RIGW uses the URL to obtain the imaging locally. The URL used it is in this form: https://hostname/dicom-web-rs/ study/1.2.840.113619.2.207.28521.42888.1640475282.450 970 [4] Domain A document source responds with multi-part encoded DICOM objects (images) as payload


**Figure XA-4: WADO-RS Retrieve URL with Domain A directly using the Retrieve URL –**


**Example of related URL values**
