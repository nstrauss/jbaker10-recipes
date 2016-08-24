/* ecPanelController */

#import <Cocoa/Cocoa.h>

@interface ecPanelController : NSObject
{
    IBOutlet NSButton *altBtn;
    IBOutlet NSButton *defBtn;
    IBOutlet NSTextField *msgText;
    IBOutlet NSButton *othBtn;
    IBOutlet NSImageCell *msgIcon;
	
	NSWindow *ecPanelWindow;
	int m_resultCode;
}
- (IBAction)doAltBtn:(id)sender;
- (IBAction)doDefBtn:(id)sender;
- (IBAction)doOthBtn:(id)sender;

- (void)done;
- (void)setResultCode:(int)code;
- (int)resultCode;
- (void)setTitle:(NSString *)str;
- (void)setMessage:(NSString *)str;
- (void)setAltBtnText:(NSString *)str;
- (void)setDefBtnText:(NSString *)str;
- (void)setOthBtnText:(NSString *)str;
- (NSWindow *)ecPanelWindow;
- (int)showSheetOnWindow:(NSWindow *)win title:(NSString *)title msg:(NSString *)msg
			defBtn:(NSString *)def altBtn:(NSString *)alt othBtn:(NSString *)oth;
@end
